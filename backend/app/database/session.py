from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import declarative_base

from app.core.config import settings

engine = create_async_engine(
    settings.database_url,
    echo=False,
    future=True,
)

AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

Base = declarative_base()


async def get_db():
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def _migrate_learner_mastery_schema(conn) -> None:
    """Recreate learner mastery table if legacy single-column unique on concept_id exists."""
    try:
        result = await conn.execute(
            text("SELECT sql FROM sqlite_master WHERE type='table' AND name='learner_concept_mastery'")
        )
        row = result.fetchone()
        if not row or not row[0]:
            return
        ddl = row[0]
        if "uq_learner_concept_mastery_user_concept" in ddl:
            return
        if "concept_id" in ddl and "UNIQUE" in ddl:
            await conn.execute(text("DROP INDEX IF EXISTS ix_learner_concept_mastery_id"))
            await conn.execute(text("ALTER TABLE learner_concept_mastery RENAME TO learner_concept_mastery_old"))
            await conn.run_sync(Base.metadata.tables["learner_concept_mastery"].create)
            await conn.execute(
                text(
                    """
                    INSERT INTO learner_concept_mastery (
                        id, user_id, concept_id, mastery_score, total_attempts, correct_attempts,
                        accuracy, recent_accuracy, difficulty_distribution, last_attempted,
                        consecutive_correct, consecutive_incorrect, confidence, learning_status,
                        created_at, updated_at
                    )
                    SELECT
                        id, user_id, concept_id, mastery_score, total_attempts, correct_attempts,
                        accuracy, recent_accuracy, difficulty_distribution, last_attempted,
                        consecutive_correct, consecutive_incorrect, confidence, learning_status,
                        created_at, updated_at
                    FROM learner_concept_mastery_old
                    """
                )
            )
            await conn.execute(text("DROP TABLE IF EXISTS learner_concept_mastery_old"))
    except Exception as e:
        print(f"Migration note: {e}")


async def init_db():
    from app.models import (  # noqa: F401 — register models
        activity,
        concept,
        document,
        quiz,
        study_plan,
        summary,
        user,
    )

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        # SQLite create_all does not add columns to existing local databases.
        user_columns = await conn.execute(text("PRAGMA table_info(users)"))
        existing_user_columns = {row[1] for row in user_columns.fetchall()}
        if "password_hash" not in existing_user_columns:
            await conn.execute(text("ALTER TABLE users ADD COLUMN password_hash VARCHAR"))
        # Legacy email indexes were case-sensitive; the index enforces normalized uniqueness too.
        await conn.execute(text("CREATE UNIQUE INDEX IF NOT EXISTS uq_users_email_lower ON users (lower(email))"))
        await _migrate_learner_mastery_schema(conn)


async def ensure_auth_schema():
    """Small idempotent compatibility migration for existing SQLite databases."""
    async with engine.begin() as conn:
        result = await conn.execute(text("PRAGMA table_info(users)"))
        columns = {row[1] for row in result.fetchall()}
        if "password_hash" not in columns:
            await conn.execute(text("ALTER TABLE users ADD COLUMN password_hash VARCHAR"))
