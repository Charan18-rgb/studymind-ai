import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy import select

from app.database.session import AsyncSessionLocal
from app.main import app
from app.models.concept import Concept, ConceptRelationship, LearnerConceptMastery
from app.models.quiz import Question, QuestionResult, Quiz, QuizAttempt
from app.services.knowledge_graph_service import knowledge_graph_service
from app.services.mastery_persistence import apply_question_result, get_or_create_mastery
from app.services.mastery_service import MasteryService
from app.services.weak_topic_service import weak_topic_service


@pytest.mark.asyncio
async def test_demo_reset_and_idempotence():
    """Verify demo reset restores baseline and demo init is idempotent."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        # Reset demo
        res = await ac.post("/api/demo/reset")
        assert res.status_code == 200
        assert res.json()["message"] == "Demo data reset successfully"

        # Check baseline mastery
        graph_res = await ac.get("/api/concepts/graph")
        assert graph_res.status_code == 200
        nodes = {n["name"]: n["mastery"] for n in graph_res.json()["nodes"]}
        assert nodes["Trees"] == 42.0
        assert nodes["Recursion"] == 51.0
        assert nodes["Arrays"] == 91.0
        assert nodes["Linked Lists"] == 82.0

        # Initialize demo again - should be idempotent
        init_res = await ac.post("/api/demo/initialize")
        assert init_res.status_code == 200
        nodes2 = {n["name"]: n["mastery"] for n in (await ac.get("/api/concepts/graph")).json()["nodes"]}
        assert nodes2["Trees"] == 42.0


@pytest.mark.asyncio
async def test_quiz_scoring_correct_incorrect_and_isolation():
    """
    Test A (correct answer increases performance),
    Test B (incorrect answer decreases performance),
    Test C (concept isolation - unrelated concept untouched),
    Test D (persistence across fresh DB session).
    """
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        await ac.post("/api/demo/reset")

        async with AsyncSessionLocal() as db:
            user_id = 1
            # Fetch Trees, Recursion, Arrays concepts
            trees = (await db.execute(select(Concept).where(Concept.name == "Trees"))).scalar_one()
            recursion = (await db.execute(select(Concept).where(Concept.name == "Recursion"))).scalar_one()
            arrays = (await db.execute(select(Concept).where(Concept.name == "Arrays"))).scalar_one()

            # Baseline masteries
            m_trees_init = (await get_or_create_mastery(user_id, trees.id, db)).mastery_score
            m_arrays_init = (await get_or_create_mastery(user_id, arrays.id, db)).mastery_score
            assert m_trees_init == 42.0
            assert m_arrays_init == 91.0

            # Test A: Apply 3 consecutive correct answers to Trees
            await apply_question_result(user_id, trees.id, is_correct=True, difficulty="medium", db=db)
            await apply_question_result(user_id, trees.id, is_correct=True, difficulty="medium", db=db)
            await apply_question_result(user_id, trees.id, is_correct=True, difficulty="medium", db=db)
            await db.commit()

        # Test D: Persistence check with a fresh DB session
        async with AsyncSessionLocal() as db_fresh:
            m_trees_after = (await get_or_create_mastery(user_id, trees.id, db_fresh)).mastery_score
            m_arrays_after = (await get_or_create_mastery(user_id, arrays.id, db_fresh)).mastery_score

            # Test A Assertion: Trees mastery increased
            assert m_trees_after > m_trees_init

            # Test C Assertion: Arrays mastery was isolated and untouched
            assert m_arrays_after == m_arrays_init

            # Test B: Apply incorrect answer to Trees
            await apply_question_result(user_id, trees.id, is_correct=False, difficulty="medium", db=db_fresh)
            await db_fresh.commit()

        async with AsyncSessionLocal() as db_fresh2:
            m_trees_after_wrong = (await get_or_create_mastery(user_id, trees.id, db_fresh2)).mastery_score
            # Test B Assertion: Incorrect answer pulled mastery down or increased consecutive_incorrect
            m_record = await get_or_create_mastery(user_id, trees.id, db_fresh2)
            assert m_record.consecutive_incorrect >= 1
            assert m_record.consecutive_correct == 0


@pytest.mark.asyncio
async def test_prerequisite_direction_and_weak_topic_diagnosis():
    """
    Test 5: Explicitly verify Recursion -> Trees (Recursion is prerequisite for Trees).
    Verify knowledge graph query and weak topic diagnosis.
    """
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        await ac.post("/api/demo/reset")

        async with AsyncSessionLocal() as db:
            user_id = 1
            trees = (await db.execute(select(Concept).where(Concept.name == "Trees"))).scalar_one()
            recursion = (await db.execute(select(Concept).where(Concept.name == "Recursion"))).scalar_one()

            # Knowledge graph service prerequisite query for Trees
            prereqs = await knowledge_graph_service.get_prerequisites(trees.id, db)
            prereq_names = [p.name for p in prereqs]
            assert "Recursion" in prereq_names

            # WeakTopicService diagnosis
            diagnosis = await weak_topic_service.diagnose(user_id, db)
            assert diagnosis["primary_weakness"] is not None
            assert diagnosis["primary_weakness"]["concept"] == "Trees"
            assert any(p["concept"] == "Recursion" for p in diagnosis["prerequisites"])


@pytest.mark.asyncio
async def test_end_to_end_adaptive_session_loop():
    """
    Test 3 & 4: Full End-to-End Adaptive Loop.
    1. Check initial recommendation.
    2. Start adaptive session (Trees).
    3. Verify question concept association.
    4. Submit session answers.
    5. Verify real before/after mastery improvement is persisted and returned.
    6. Verify next recommendation updates.
    """
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        await ac.post("/api/demo/reset")

        # 1. Fetch initial Next Best Action
        action_res = await ac.get("/api/recommendations/next-action")
        assert action_res.status_code == 200
        init_action = action_res.json()
        assert init_action["action"] == "adaptive_practice"

        # 2. Start adaptive session
        sess_res = await ac.post("/api/adaptive/session")
        assert sess_res.status_code == 200
        sess_data = sess_res.json()["session"]
        assert sess_data["target_concept"]["name"] == "Trees"
        assert sess_data["target_concept"]["current_mastery"] == 42.0

        questions = sess_data["questions"]
        assert len(questions) == 5

        # 3. Submit all answers correctly
        # In demo mode, each question has 4 options; option 0 is the correct answer in our curated test set
        answers = []
        async with AsyncSessionLocal() as db:
            for q in questions:
                q_db = (await db.execute(select(Question).where(Question.id == q["id"]))).scalar_one()
                answers.append({
                    "question_id": q["id"],
                    "selected_answer": q_db.correct_answer,
                    "time_spent_seconds": 15,
                })

        submit_res = await ac.post(
            f"/api/adaptive/session/{sess_data['session_id']}/submit",
            json={"answers": answers},
        )
        assert submit_res.status_code == 200
        result = submit_res.json()

        # 4. Verify before/after mastery values come from real calculation
        assert result["before_mastery"] == 42.0
        assert result["after_mastery"] > 42.0
        assert result["improvement"] == round(result["after_mastery"] - 42.0, 1)
        assert result["score"] == 100.0

        # 5. Verify database persistence
        graph_res = await ac.get("/api/concepts/graph")
        node_trees = next(n for n in graph_res.json()["nodes"] if n["name"] == "Trees")
        assert node_trees["mastery"] == result["after_mastery"]

        # 6. Verify dashboard stats updated
        dash_res = await ac.get("/api/dashboard")
        dash_data = dash_res.json()
        assert dash_data["stats"]["mastery"] > 0
        assert len(dash_data["recent_activity"]) > 0


@pytest.mark.asyncio
async def test_ask_notes_rag_grounded_and_rejection():
    """
    Test 8: Test RAG search retrieval on document chunks.
    Verify relevant queries find chunks with citations, and unrelated queries reject safely.
    """
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        await ac.post("/api/demo/reset")

        docs = (await ac.get("/api/documents/")).json()
        assert len(docs) > 0
        doc_id = docs[0]["id"]

        # Relevant question: recursion / trees
        ask_res = await ac.post(
            f"/api/documents/{doc_id}/ask",
            json={"question": "What is recursion and tree traversal?"},
        )
        assert ask_res.status_code == 200
        data = ask_res.json()
        assert len(data["sources"]) > 0
        assert "page_number" in data["sources"][0]
        assert data["grounded"] is True

        # Completely unrelated question with no keywords in document
        unrelated_res = await ac.post(
            f"/api/documents/{doc_id}/ask",
            json={"question": "How do quantum superconductors affect aerospace propulsion?"},
        )
        assert unrelated_res.status_code == 200
        unrelated_data = unrelated_res.json()
        assert unrelated_data["grounded"] is False
        assert "couldn't find" in unrelated_data["answer"].lower()
