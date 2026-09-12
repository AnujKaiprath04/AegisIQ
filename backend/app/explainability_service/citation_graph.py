from typing import Any, Dict, List
from app.explainability_service.types import (
    CitationEdge,
    CitationGraph,
    CitationNode,
    NodeType,
)
from app.rag_engine.types import RAGCitation


class CitationGraphBuilder:
    """Builds a Directed Acyclic Graph (DAG) connecting Queries, Claims, Passages, and Documents."""

    @classmethod
    def build_graph(
        cls,
        query: str,
        answer: str,
        citations: List[RAGCitation],
    ) -> CitationGraph:
        nodes: List[CitationNode] = []
        edges: List[CitationEdge] = []

        # 1. Root Query Node
        query_node_id = "node-q-root"
        nodes.append(
            CitationNode(
                id=query_node_id,
                label=f"Query: {query[:60]}...",
                node_type=NodeType.QUERY,
                metadata={"full_text": query},
            )
        )

        seen_docs = set()

        for idx, cit in enumerate(citations):
            claim_id = f"node-claim-{idx + 1}"
            pass_id = f"node-pass-{idx + 1}"
            doc_id = f"node-doc-{cit.document_title.lower().replace(' ', '-')}"

            # 2. Claim Node
            claim_label = f"Claim [{cit.source_id}]: {cit.snippet[:45]}..."
            nodes.append(
                CitationNode(
                    id=claim_id,
                    label=claim_label,
                    node_type=NodeType.CLAIM,
                    metadata={"source_id": cit.source_id, "section": cit.section},
                )
            )
            edges.append(
                CitationEdge(
                    source_id=query_node_id,
                    target_id=claim_id,
                    relation="ASSERTS_CLAIM",
                    weight=1.0,
                )
            )

            # 3. Passage Node
            nodes.append(
                CitationNode(
                    id=pass_id,
                    label=f"Passage (Score: {cit.relevance_score * 100:.1f}%)",
                    node_type=NodeType.PASSAGE,
                    metadata={"snippet": cit.snippet, "relevance_score": cit.relevance_score},
                )
            )
            edges.append(
                CitationEdge(
                    source_id=claim_id,
                    target_id=pass_id,
                    relation="SUPPORTED_BY",
                    weight=cit.relevance_score,
                )
            )

            # 4. Master Document Node
            if doc_id not in seen_docs:
                seen_docs.add(doc_id)
                nodes.append(
                    CitationNode(
                        id=doc_id,
                        label=f"Doc: {cit.document_title}",
                        node_type=NodeType.DOCUMENT,
                        metadata={"title": cit.document_title, "department": cit.department},
                    )
                )

            edges.append(
                CitationEdge(
                    source_id=pass_id,
                    target_id=doc_id,
                    relation="EXTRACTED_FROM",
                    weight=1.0,
                )
            )

        return CitationGraph(
            nodes=nodes,
            edges=edges,
            total_nodes=len(nodes),
            total_edges=len(edges),
        )
