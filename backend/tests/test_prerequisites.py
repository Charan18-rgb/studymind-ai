import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.database.session import Base
from app.models.concept import Concept, ConceptRelationship
from app.services.knowledge_graph_service import knowledge_graph_service


@pytest_asyncio.fixture
async def db_session():
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    session_factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with session_factory() as session:
        trees = Concept(document_id=1, name="Trees", description="")
        recursion = Concept(document_id=1, name="Recursion", description="")
        session.add_all([trees, recursion])
        await session.flush()
        session.add(
            ConceptRelationship(
                source_concept_id=recursion.id,
                target_concept_id=trees.id,
                relationship_type="prerequisite",
            )
        )
        await session.commit()

        async with session_factory() as s2:
            yield s2, trees.id

    await engine.dispose()


@pytest.mark.asyncio
async def test_prerequisite_direction(db_session):
    session, trees_id = db_session
    prereqs = await knowledge_graph_service.get_prerequisites(trees_id, session)
    names = [p.name for p in prereqs]
    assert "Recursion" in names
