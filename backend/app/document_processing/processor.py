import re
from typing import Any, Dict, List, Tuple
import pymupdf  # PyMuPDF


class DocumentProcessor:
    """Process PDF documents and extract text with page metadata and chunking."""

    def __init__(self, chunk_size: int = 1000, chunk_overlap: int = 200):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def extract_pages_from_pdf(self, file_path: str) -> List[Tuple[int, str]]:
        """Extract text from each page with 1-based page numbers."""
        doc = pymupdf.open(file_path)
        pages = []
        for page_num in range(doc.page_count):
            page = doc[page_num]
            text = page.get_text()
            if text:
                pages.append((page_num + 1, text))
        doc.close()
        return pages

    def clean_text(self, text: str) -> str:
        """Clean extracted text."""
        # Replace multiple spaces with a single space while keeping line breaks reasonably clean
        text = re.sub(r'[ \t]+', ' ', text)
        return text.strip()

    def chunk_pages(self, pages: List[Tuple[int, str]]) -> List[Dict[str, Any]]:
        """Split page texts into manageable chunks with page tracking."""
        chunks: List[Dict[str, Any]] = []

        for page_num, raw_text in pages:
            clean = self.clean_text(raw_text)
            if not clean:
                continue

            text_length = len(clean)
            if text_length <= self.chunk_size:
                chunks.append({
                    "content": clean,
                    "chunk_index": len(chunks),
                    "page_number": page_num,
                })
            else:
                for i in range(0, text_length, self.chunk_size - self.chunk_overlap):
                    chunk_text = clean[i:i + self.chunk_size].strip()
                    if chunk_text:
                        chunks.append({
                            "content": chunk_text,
                            "chunk_index": len(chunks),
                            "page_number": page_num,
                        })

        return chunks

    def process_document(self, file_path: str) -> Dict[str, Any]:
        """Full document processing pipeline."""
        pages = self.extract_pages_from_pdf(file_path)
        page_count = len(pages)
        full_text = "\n\n".join([p[1] for p in pages])
        clean_full_text = self.clean_text(full_text)
        chunks = self.chunk_pages(pages)

        return {
            "text": clean_full_text,
            "page_count": max(page_count, 1),
            "chunks": chunks,
        }
