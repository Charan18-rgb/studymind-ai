from typing import List

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.ai.service import ai_service
from app.core.deps import get_current_user_id
from app.database.session import get_db
from app.models.document import Document
from app.core.config import settings
from app.schemas.document import Document as DocumentSchema
from app.schemas.document import DocumentChunk as DocumentChunkSchema
from app.services.document_service import document_service

router = APIRouter(prefix="/documents", tags=["documents"])

MAX_UPLOAD_BYTES = settings.upload_max_bytes


class AskRequest(BaseModel):
    question: str = Field(min_length=1, max_length=2000)


@router.post("/upload", response_model=DocumentSchema)
async def upload_document(
    file: UploadFile = File(...),
    title: str | None = None,
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    if not file.filename or not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported")
    if file.content_type not in ("application/pdf", "application/octet-stream"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported")

    file_data = await file.read(MAX_UPLOAD_BYTES + 1)
    if len(file_data) == 0:
        raise HTTPException(status_code=400, detail="Empty PDF file")
    if len(file_data) > MAX_UPLOAD_BYTES:
        limit_mb = max(1, MAX_UPLOAD_BYTES // (1024 * 1024))
        raise HTTPException(status_code=413, detail=f"File exceeds the {limit_mb}MB upload limit")
    if not file_data.startswith(b"%PDF-"):
        raise HTTPException(status_code=400, detail="The uploaded file is not a valid PDF")

    if not title:
        title = file.filename.replace(".pdf", "")

    return await document_service.upload_document(
        user_id=user_id,
        file_data=file_data,
        filename=file.filename,
        title=title,
        db=db,
    )


@router.get("/", response_model=List[DocumentSchema])
async def get_documents(
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Document).where(Document.user_id == user_id))
    return result.scalars().all()


@router.get("/{document_id}", response_model=DocumentSchema)
async def get_document(document_id: int, user_id: int = Depends(get_current_user_id), db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Document).where(Document.id == document_id, Document.user_id == user_id))
    document = result.scalar_one_or_none()
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    return document


@router.get("/{document_id}/chunks", response_model=List[DocumentChunkSchema])
async def get_document_chunks(document_id: int, user_id: int = Depends(get_current_user_id), db: AsyncSession = Depends(get_db)):
    owned = await db.scalar(select(Document.id).where(Document.id == document_id, Document.user_id == user_id))
    if not owned:
        raise HTTPException(status_code=404, detail="Document not found")
    return await document_service.get_document_chunks(document_id, db)


@router.post("/{document_id}/ask")
async def ask_document(
    document_id: int,
    body: AskRequest,
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    owned = await db.scalar(select(Document.id).where(Document.id == document_id, Document.user_id == user_id))
    if not owned:
        raise HTTPException(status_code=404, detail="Document not found")
    chunks = await document_service.search_chunks(document_id, body.question, db)
    if not chunks:
        return {
            "answer": "I couldn't find this information in the uploaded material.",
            "sources": [],
            "grounded": False,
        }

    chunk_texts = [c.content for c in chunks[:5]]
    sources = [
        {
            "chunk_index": c.chunk_index,
            "page_number": c.page_number,
            "excerpt": c.content[:240] + ("..." if len(c.content) > 240 else ""),
        }
        for c in chunks[:5]
    ]

    if ai_service.available:
        try:
            answer = ai_service.answer_question(body.question, chunk_texts)
        except Exception:
            raise HTTPException(status_code=503, detail="AI service temporarily unavailable")
    else:
        answer = "AI answering is temporarily unavailable. These are the matching excerpts from your document; review the cited text directly."

    grounded = "couldn't find" not in answer.lower()
    return {
        "answer": answer,
        "sources": sources,
        "grounded": grounded,
        "ai_available": ai_service.available,
        "disclaimer": "AI-generated content may contain mistakes. Verify important academic information.",
    }


@router.post("/{document_id}/search")
async def search_chunks(
    document_id: int,
    query: str,
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    owned = await db.scalar(select(Document.id).where(Document.id == document_id, Document.user_id == user_id))
    if not owned:
        raise HTTPException(status_code=404, detail="Document not found")
    chunks = await document_service.search_chunks(document_id, query, db)
    return {"chunks": chunks}
