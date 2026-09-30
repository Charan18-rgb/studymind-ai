import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy import select

from app.main import app


@pytest.mark.asyncio
async def test_auth_registration_login_and_document_isolation():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as a, AsyncClient(transport=transport, base_url="http://test") as b:
        assert (await a.get("/api/auth/me")).status_code == 401
        suffix = __import__("uuid").uuid4().hex
        email_a = f"user-a-{suffix}@example.com"
        email_b = f"user-b-{suffix}@example.com"
        registered = await a.post("/api/auth/register", json={"name": "Learner A", "email": email_a.upper(), "password": "safe-passphrase-a"})
        assert registered.status_code == 201
        assert registered.json()["email"] == email_a
        assert "password_hash" not in registered.json()
        assert "httponly" in registered.headers.get("set-cookie", "").lower()
        assert (await a.get("/api/auth/me")).json()["id"] == registered.json()["id"]
        assert (await a.post("/api/auth/register", json={"name": "Duplicate", "email": email_a, "password": "safe-passphrase-a"})).status_code == 409
        assert (await b.post("/api/auth/login", json={"email": email_a, "password": "incorrect-password"})).status_code == 401
        assert (await b.post("/api/auth/register", json={"name": "Learner B", "email": email_b, "password": "safe-passphrase-b"})).status_code == 201

        from app.database.session import AsyncSessionLocal
        from app.models.document import Document
        from app.models.concept import Concept, LearnerConceptMastery
        from app.models.quiz import Quiz, Question
        async with AsyncSessionLocal() as db:
            doc = Document(user_id=registered.json()["id"], title="Private", filename="private.pdf", file_path="private.pdf", status="ready")
            db.add(doc)
            await db.flush()
            concept = Concept(document_id=doc.id, name="Private concept", description="A-only concept")
            db.add(concept)
            await db.flush()
            db.add(LearnerConceptMastery(user_id=registered.json()["id"], concept_id=concept.id, mastery_score=63, total_attempts=1))
            quiz = Quiz(document_id=doc.id, user_id=registered.json()["id"], title="Private quiz", concepts=[concept.id])
            db.add(quiz)
            await db.flush()
            question = Question(quiz_id=quiz.id, concept_id=concept.id, question_text="Private question", options=["A"], correct_answer="A")
            db.add(question)
            await db.commit()
            await db.refresh(doc)
            concept_id, quiz_id, question_id = concept.id, quiz.id, question.id
            doc_id = doc.id
        assert (await a.get(f"/api/documents/{doc_id}")).status_code == 200
        assert (await b.get(f"/api/documents/{doc_id}")).status_code == 404
        assert (await b.post(f"/api/documents/{doc_id}/ask", json={"question": "private"})).status_code == 404
        assert (await b.get(f"/api/concepts/graph?document_id={doc_id}")).status_code == 404
        assert (await b.get(f"/api/concepts/{concept_id}")).status_code == 404
        assert (await b.get(f"/api/concepts/{concept_id}/explanation")).status_code == 404
        assert (await b.get(f"/api/quizzes/{quiz_id}")).status_code == 404
        assert (await b.post(f"/api/quizzes/{quiz_id}/submit", json={"answers": [{"question_id": question_id, "selected_answer": "A"}]})).status_code == 404
        assert (await b.get("/api/concepts/learner/mastery")).json() == []
        assert (await a.post("/api/auth/logout")).status_code == 200
        assert (await a.get("/api/auth/me")).status_code == 401
        assert (await a.get("/api/documents/")).status_code == 401


@pytest.mark.asyncio
async def test_new_user_empty_state_and_invalid_upload():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        suffix = __import__("uuid").uuid4().hex
        await client.post("/api/auth/register", json={"name": "Fresh Learner", "email": f"fresh-{suffix}@example.com", "password": "safe-passphrase"})
        dashboard = (await client.get("/api/dashboard")).json()
        assert dashboard["stats"]["mastery"] == 0
        assert dashboard["weak_topics"] == []
        graph = (await client.get("/api/concepts/graph")).json()
        assert graph["nodes"] == []
        assert (await client.post("/api/documents/upload", files={"file": ("fake.pdf", b"not a pdf", "application/pdf")})).status_code == 400


def test_ai_service_unconfigured_and_structured_response_validation(monkeypatch):
    from app.ai.service import AIService
    from app.core.config import settings

    monkeypatch.setattr(settings, "gemini_api_key", "")
    service = AIService()
    assert service.available is False
    with pytest.raises(RuntimeError, match="not configured"):
        service.answer_question("question", ["source text"])
    with pytest.raises(ValueError, match="malformed"):
        service._parse_json_response("not-json")
    with pytest.raises(ValueError, match="object"):
        service._parse_json_response("[]")


@pytest.mark.asyncio
async def test_ai_extraction_failure_keeps_chunks_and_does_not_persist_partial_graph(monkeypatch, tmp_path):
    import fitz
    from app.ai.service import ai_service
    from app.core.config import settings
    from app.database.session import AsyncSessionLocal
    from app.models.document import Document, DocumentChunk
    from app.models.concept import Concept, ConceptRelationship
    from app.models.user import User
    from app.api.auth import hash_password
    from app.services.document_service import DocumentService

    pdf_path = tmp_path / "lesson.pdf"
    pdf = fitz.open()
    page = pdf.new_page()
    page.insert_text((72, 72), "A unique lesson explains hashing, collisions, and bucket chaining.")
    pdf.save(pdf_path)
    pdf.close()

    previous_available = ai_service.available
    previous_upload_dir = settings.upload_directory
    monkeypatch.setattr(ai_service, "available", True)
    monkeypatch.setattr(ai_service, "extract_concepts", lambda text: [
        {"name": "Hashing", "description": "Map keys", "difficulty": "medium", "importance": 0.8}
    ])
    monkeypatch.setattr(ai_service, "extract_relationships", lambda names, text: (_ for _ in ()).throw(RuntimeError("provider unavailable")))
    monkeypatch.setattr(settings, "upload_directory", str(tmp_path / "uploads"))
    try:
        async with AsyncSessionLocal() as db:
            test_user = User(
                email=f"ai-failure-{__import__('uuid').uuid4().hex}@example.com",
                name="AI failure test",
                password_hash=hash_password("safe-test-password"),
            )
            db.add(test_user)
            await db.flush()
            document = await DocumentService().upload_document(
                user_id=test_user.id,
                file_data=pdf_path.read_bytes(),
                filename="lesson.pdf",
                title="Hashing lesson",
                db=db,
            )
            assert document.status == "ai_unavailable"
            assert await db.scalar(select(DocumentChunk.id).where(DocumentChunk.document_id == document.id))
            assert await db.scalar(select(Concept.id).where(Concept.document_id == document.id)) is None
            assert await db.scalar(select(ConceptRelationship.id).where(
                ConceptRelationship.source_concept_id.in_(select(Concept.id).where(Concept.document_id == document.id))
            )) is None
    finally:
        ai_service.available = previous_available
        settings.upload_directory = previous_upload_dir
