import pytest
from httpx import ASGITransport, AsyncClient
from app.main import app


@pytest.mark.asyncio
async def test_health_and_root():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        res = await ac.get("/health")
        assert res.status_code == 200
        assert res.json() == {"status": "healthy"}

        root_res = await ac.get("/")
        assert root_res.status_code == 200
        assert root_res.json()["status"] == "running"


@pytest.mark.asyncio
async def test_demo_init_and_dashboard():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        # 1. Reset / Init demo
        init_res = await ac.post("/api/demo/initialize")
        assert init_res.status_code == 200

        # 2. Get dashboard
        dash_res = await ac.get("/api/dashboard")
        assert dash_res.status_code == 200
        dash_data = dash_res.json()
        assert "next_best_action" in dash_data
        assert dash_data["next_best_action"]["action"] in ("adaptive_practice", "upload", "quiz")
        assert len(dash_data["weak_topics"]) > 0

        # 3. Knowledge Graph
        graph_res = await ac.get("/api/concepts/graph")
        assert graph_res.status_code == 200
        graph_data = graph_res.json()
        assert len(graph_data["nodes"]) >= 7
        assert len(graph_data["edges"]) >= 5

        # 4. Adaptive Explanation
        tree_node = next((n for n in graph_data["nodes"] if n["name"] == "Trees"), None)
        assert tree_node is not None
        exp_res = await ac.get(f"/api/concepts/{tree_node['id']}/explanation")
        assert exp_res.status_code == 200
        exp_data = exp_res.json()
        assert "simple_explanation" in exp_data
        assert "real_world_analogy" in exp_data

        # 5. Adaptive Session Creation
        session_res = await ac.post("/api/adaptive/session")
        assert session_res.status_code == 200
        session_data = session_res.json()
        assert session_data["session"] is not None
        session = session_data["session"]
        assert len(session["questions"]) > 0

        # 6. Adaptive Session Submission
        session_id = session["session_id"]
        answers = [
            {"question_id": q["id"], "selected_answer": "Store hierarchical data", "time_spent_seconds": 10}
            if "purpose" in q["question_text"].lower()
            else {"question_id": q["id"], "selected_answer": q.get("options", ["A"])[0], "time_spent_seconds": 10}
            for q in session["questions"]
        ]
        submit_res = await ac.post(f"/api/adaptive/session/{session_id}/submit", json={"answers": answers})
        assert submit_res.status_code == 200
        submit_data = submit_res.json()
        assert "before_mastery" in submit_data
        assert "after_mastery" in submit_data

        # 7. Study Plan
        plan_res = await ac.get("/api/study-plans/current")
        assert plan_res.status_code == 200
        plan_data = plan_res.json()
        assert len(plan_data["items"]) > 0

        # 8. Analytics
        analytics_res = await ac.get("/api/analytics")
        assert analytics_res.status_code == 200
        analytics_data = analytics_res.json()
        assert "metrics" in analytics_data
        assert len(analytics_data["topic_mastery"]) >= 7
