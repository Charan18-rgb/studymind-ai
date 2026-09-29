import os
import re
from typing import Any, Dict, List, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.ai.service import ai_service
from app.document_processing.processor import DocumentProcessor
from app.models.concept import Concept, ConceptRelationship
from app.models.document import Document, DocumentChunk
from app.schemas.document import DocumentChunk as DocumentChunkSchema


class DocumentService:
    """Service for document processing, chunking, concept extraction, and RAG retrieval."""

    def __init__(self):
        self.processor = DocumentProcessor()

    async def upload_document(
        self,
        user_id: int,
        file_data: bytes,
        filename: str,
        title: str,
        db: AsyncSession,
    ) -> Document:
        """Upload and process a new PDF document."""
        os.makedirs("data", exist_ok=True)
        file_path = f"data/{filename}"
        with open(file_path, "wb") as f:
            f.write(file_data)

        document = Document(
            user_id=user_id,
            title=title,
            filename=filename,
            file_path=file_path,
            status="processing",
        )
        db.add(document)
        await db.flush()

        await self._process_document(document.id, file_path, db)
        await db.commit()
        await db.refresh(document)
        return document

    async def _process_document(
        self,
        document_id: int,
        file_path: str,
        db: AsyncSession,
    ) -> None:
        """Extract text, chunk with page numbers, and extract concepts & relationships."""
        try:
            processed = self.processor.process_document(file_path)

            result = await db.execute(select(Document).where(Document.id == document_id))
            document = result.scalar_one_or_none()
            if document:
                document.page_count = processed["page_count"]
                document.status = "processing"
                await db.flush()

            # Store Chunks
            for chunk_data in processed["chunks"]:
                chunk = DocumentChunk(
                    document_id=document_id,
                    chunk_index=chunk_data["chunk_index"],
                    content=chunk_data["content"],
                    page_number=chunk_data.get("page_number", 1),
                )
                db.add(chunk)
            await db.flush()

            # Extract concepts using AI if available
            if ai_service.available:
                try:
                    concepts_data = ai_service.extract_concepts(processed["text"])
                    concept_map: Dict[str, Concept] = {}

                    for concept_data in concepts_data:
                        concept = Concept(
                            document_id=document_id,
                            name=concept_data["name"],
                            description=concept_data.get("description"),
                            difficulty=concept_data.get("difficulty", "medium"),
                            estimated_importance=concept_data.get("importance", 0.5),
                        )
                        db.add(concept)
                        await db.flush()
                        concept_map[concept.name.lower()] = concept

                    concept_names = [c["name"] for c in concepts_data]
                    relationships_data = ai_service.extract_relationships(
                        concept_names, processed["text"]
                    )

                    for rel_data in relationships_data:
                        src_name = rel_data.get("source", "").lower()
                        tgt_name = rel_data.get("target", "").lower()
                        src_concept = concept_map.get(src_name)
                        tgt_concept = concept_map.get(tgt_name)

                        if src_concept and tgt_concept and src_concept.id != tgt_concept.id:
                            rel = ConceptRelationship(
                                source_concept_id=src_concept.id,
                                target_concept_id=tgt_concept.id,
                                relationship_type=rel_data.get("relationship_type", rel_data.get("type", "related")),
                                confidence=rel_data.get("confidence", 0.8),
                            )
                            db.add(rel)
                    await db.flush()
                except Exception as ai_err:
                    print(f"AI concept extraction warning: {ai_err}")

            if document:
                document.status = "ready"
                await db.flush()

        except Exception as e:
            print(f"Document processing error: {e}")
            result = await db.execute(select(Document).where(Document.id == document_id))
            document = result.scalar_one_or_none()
            if document:
                document.status = "error"
                await db.flush()

    async def get_document_chunks(
        self,
        document_id: int,
        db: AsyncSession,
    ) -> List[DocumentChunkSchema]:
        """Get all chunks for a document."""
        result = await db.execute(
            select(DocumentChunk)
            .where(DocumentChunk.document_id == document_id)
            .order_by(DocumentChunk.chunk_index.asc())
        )
        chunks = result.scalars().all()
        return [DocumentChunkSchema.model_validate(chunk) for chunk in chunks]

    async def search_chunks(
        self,
        document_id: int,
        query: str,
        db: AsyncSession,
    ) -> List[DocumentChunkSchema]:
        """
        RAG chunk search with multi-word token overlap and relevance ranking.
        """
        result = await db.execute(
            select(DocumentChunk).where(DocumentChunk.document_id == document_id)
        )
        all_chunks = list(result.scalars().all())
        if not all_chunks:
            return []

        # Tokenize query removing common stop words
        stop_words = {
            "what", "is", "the", "a", "an", "and", "or", "in", "of", "to", "for",
            "how", "why", "does", "do", "can", "explain", "tell", "me", "about",
            "with", "which", "are", "on", "at", "by", "from",
        }
        tokens = [
            t.lower()
            for t in re.findall(r'\b\w+\b', query)
            if len(t) > 2 and t.lower() not in stop_words
        ]

        if not tokens:
            # Return first few chunks as context
            return [DocumentChunkSchema.model_validate(c) for c in all_chunks[:5]]

        scored_chunks = []
        for chunk in all_chunks:
            content_lower = chunk.content.lower()
            score = 0
            for token in tokens:
                if token in content_lower:
                    score += content_lower.count(token) * 2

            if score > 0:
                scored_chunks.append((score, chunk))

        scored_chunks.sort(key=lambda x: x[0], reverse=True)

        if scored_chunks:
            top_chunks = [c for _, c in scored_chunks[:5]]
            return [DocumentChunkSchema.model_validate(c) for c in top_chunks]

        # If no strict keyword matches, return empty to trigger grounded rejection
        return []


document_service = DocumentService()
