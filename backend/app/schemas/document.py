from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class DocumentBase(BaseModel):
    title: str
    filename: str


class DocumentCreate(DocumentBase):
    pass


class Document(DocumentBase):
    id: int
    page_count: int
    status: str
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class DocumentChunkBase(BaseModel):
    chunk_index: int
    content: str
    page_number: Optional[int] = None


class DocumentChunk(DocumentChunkBase):
    id: int
    document_id: int
    created_at: datetime

    class Config:
        from_attributes = True
