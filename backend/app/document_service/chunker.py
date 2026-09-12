import re
from typing import Any, Dict, List, Optional
from pydantic import BaseModel


class SemanticChunk(BaseModel):
    chunk_index: int
    content: str
    token_count: int
    char_length: int
    char_start: int
    char_end: int
    section_header: Optional[str] = None


class RecursiveSemanticChunker:
    """Splits text recursively based on semantic boundaries with configurable token overlap."""

    def __init__(self, chunk_size: int = 500, chunk_overlap: int = 80):
        self.chunk_size = max(100, chunk_size)
        self.chunk_overlap = max(0, min(chunk_overlap, self.chunk_size // 2))

    def _estimate_tokens(self, text: str) -> int:
        return max(1, len(text.split()))

    def chunk_text(self, text: str, default_header: Optional[str] = None) -> List[SemanticChunk]:
        if not text or not text.strip():
            return []

        text = text.strip()
        chunks: List[SemanticChunk] = []
        
        # Determine paragraph blocks
        paragraphs = re.split(r"(\n\n+)", text)
        current_chunk_text = ""
        current_header = default_header or "General Section"
        char_cursor = 0

        for block in paragraphs:
            if not block.strip():
                continue

            # Detect header markers
            if block.startswith("#") or block.startswith("[Page") or block.startswith("[Slide"):
                current_header = block.split("\n")[0].replace("#", "").strip()

            if len(current_chunk_text) + len(block) <= self.chunk_size:
                current_chunk_text += ("\n\n" if current_chunk_text else "") + block
            else:
                if current_chunk_text:
                    chunk_len = len(current_chunk_text)
                    chunks.append(
                        SemanticChunk(
                            chunk_index=len(chunks) + 1,
                            content=current_chunk_text.strip(),
                            token_count=self._estimate_tokens(current_chunk_text),
                            char_length=chunk_len,
                            char_start=char_cursor,
                            char_end=char_cursor + chunk_len,
                            section_header=current_header,
                        )
                    )
                    char_cursor += chunk_len - self.chunk_overlap
                    # Keep overlap tail
                    overlap_seed = current_chunk_text[-self.chunk_overlap :] if self.chunk_overlap > 0 else ""
                    current_chunk_text = overlap_seed + "\n\n" + block
                else:
                    # Single block exceeds chunk size -> split by sentence
                    sentences = re.split(r"(?<=[.?!]) +", block)
                    for sent in sentences:
                        if len(current_chunk_text) + len(sent) <= self.chunk_size:
                            current_chunk_text += (" " if current_chunk_text else "") + sent
                        else:
                            if current_chunk_text:
                                chunk_len = len(current_chunk_text)
                                chunks.append(
                                    SemanticChunk(
                                        chunk_index=len(chunks) + 1,
                                        content=current_chunk_text.strip(),
                                        token_count=self._estimate_tokens(current_chunk_text),
                                        char_length=chunk_len,
                                        char_start=char_cursor,
                                        char_end=char_cursor + chunk_len,
                                        section_header=current_header,
                                    )
                                )
                                char_cursor += chunk_len - self.chunk_overlap
                                overlap_seed = current_chunk_text[-self.chunk_overlap :] if self.chunk_overlap > 0 else ""
                                current_chunk_text = overlap_seed + " " + sent
                            else:
                                current_chunk_text = sent

        if current_chunk_text.strip():
            chunk_len = len(current_chunk_text)
            chunks.append(
                SemanticChunk(
                    chunk_index=len(chunks) + 1,
                    content=current_chunk_text.strip(),
                    token_count=self._estimate_tokens(current_chunk_text),
                    char_length=chunk_len,
                    char_start=char_cursor,
                    char_end=char_cursor + chunk_len,
                    section_header=current_header,
                )
            )

        return chunks
