from typing import Any, Dict, List, Tuple
from app.vector_service.types import VectorSearchResult
from app.rag_engine.types import CompressedPassage, RAGCitation


class ContextCompressor:
    """Filters, deduplicates, and compresses retrieved vector chunks within token budgets."""

    @classmethod
    def compress_and_rank(
        cls,
        raw_results: List[Dict[str, Any]],
        min_relevance_threshold: float = 0.50,
        max_tokens_budget: int = 1500,
    ) -> Tuple[List[CompressedPassage], List[RAGCitation]]:
        filtered_passages: List[CompressedPassage] = []
        citations: List[RAGCitation] = []
        accumulated_tokens = 0
        seen_texts = set()

        for idx, item in enumerate(raw_results):
            score = item.get("score", 0.0)
            if score < min_relevance_threshold:
                continue

            doc_text = item.get("document", "").strip()
            if not doc_text or doc_text in seen_texts:
                continue

            token_estimate = max(1, len(doc_text.split()))
            if accumulated_tokens + token_estimate > max_tokens_budget and len(filtered_passages) >= 2:
                break

            seen_texts.add(doc_text)
            accumulated_tokens += token_estimate
            meta = item.get("metadata", {})

            passage_id = item.get("id", f"p-{idx + 1}")
            filtered_passages.append(
                CompressedPassage(
                    passage_id=passage_id,
                    content=doc_text,
                    score=score,
                    metadata=meta,
                )
            )

            # Build Citation
            doc_title = meta.get("title", meta.get("document_title", "Enterprise Document"))
            dept = meta.get("department", "EXECUTIVE")
            sec = meta.get("section", meta.get("category", "General Policy"))

            snippet = doc_text[:180] + ("..." if len(doc_text) > 180 else "")

            citations.append(
                RAGCitation(
                    source_id=len(citations) + 1,
                    document_title=doc_title,
                    section=str(sec),
                    department=str(dept),
                    relevance_score=round(score, 4),
                    snippet=snippet,
                )
            )

        return filtered_passages, citations
