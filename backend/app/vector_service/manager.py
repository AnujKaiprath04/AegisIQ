import time
import logging
from typing import Any, Dict, List, Optional

from app.vector_service.store import VectorStoreFactory
from app.vector_service.types import CollectionInfo, DistanceMetric, VectorSearchResult
from app.embedding_service.engine import EmbeddingEngine
from app.document_service.repository import SEEDED_KNOWLEDGE_DOCS

logger = logging.getLogger("aegisiq.vector_service.manager")


class VectorStoreManager:
    """Orchestrates collection lifecycle, document indexing, and semantic similarity queries."""

    _seeded: bool = False

    @classmethod
    def initialize_and_seed(cls):
        """Pre-seed vector collections with default enterprise knowledge base vectors."""
        if cls._seeded:
            return

        store = VectorStoreFactory.get_store()
        
        # 1. Create standard collections
        store.create_collection("enterprise_knowledge", 384, DistanceMetric.COSINE, "Unified enterprise knowledge repository.")
        store.create_collection("security_policies", 384, DistanceMetric.COSINE, "ISO 27001 and cybersecurity policy documents.")
        store.create_collection("financial_reports", 384, DistanceMetric.COSINE, "Q1 financial filings, revenue, and general ledger reports.")
        store.create_collection("legal_slas", 384, DistanceMetric.COSINE, "Master SLA agreements and contractual terms.")

        # 2. Populate seeded knowledge documents
        doc_texts = []
        doc_ids = []
        doc_metas = []

        for idx, doc in enumerate(SEEDED_KNOWLEDGE_DOCS):
            doc_id = f"chunk-seed-{idx + 1}"
            doc_text = f"Title: {doc['title']}\nDepartment: {doc['department']}\nContent: {doc['summary_text']}"
            doc_meta = {
                "document_id": idx + 1,
                "title": doc["title"],
                "department": doc["department"],
                "category": doc["category"],
                "file_format": doc["file_format"],
                "version": doc["version"],
            }
            doc_ids.append(doc_id)
            doc_texts.append(doc_text)
            doc_metas.append(doc_meta)

        # Generate vectors using Embedding Engine
        embed_res = EmbeddingEngine.generate_embeddings(doc_texts)
        vectors = embed_res["embeddings"]

        # Upsert into master collection
        store.upsert("enterprise_knowledge", doc_ids, vectors, doc_texts, doc_metas)

        # Upsert into department specific collections
        for d_id, vec, text, meta in zip(doc_ids, vectors, doc_texts, doc_metas):
            if meta["department"] == "SECURITY":
                store.upsert("security_policies", [d_id], [vec], [text], [meta])
            elif meta["department"] == "FINANCE":
                store.upsert("financial_reports", [d_id], [vec], [text], [meta])
            elif meta["department"] == "LEGAL":
                store.upsert("legal_slas", [d_id], [vec], [text], [meta])

        cls._seeded = True
        logger.info("Seeded 4 enterprise vector collections successfully.")

    @classmethod
    def list_collections(cls) -> List[CollectionInfo]:
        cls.initialize_and_seed()
        store = VectorStoreFactory.get_store()
        return store.list_collections()

    @classmethod
    def create_collection(
        cls,
        name: str,
        dimensions: int = 384,
        description: Optional[str] = None,
    ) -> CollectionInfo:
        cls.initialize_and_seed()
        store = VectorStoreFactory.get_store()
        return store.create_collection(name=name, dimensions=dimensions, metric=DistanceMetric.COSINE, description=description)

    @classmethod
    def delete_collection(cls, name: str) -> bool:
        cls.initialize_and_seed()
        store = VectorStoreFactory.get_store()
        return store.delete_collection(name)

    @classmethod
    def upsert_chunks(
        cls,
        collection_name: str,
        chunk_texts: List[str],
        metadatas: Optional[List[Dict[str, Any]]] = None,
        custom_ids: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        cls.initialize_and_seed()
        store = VectorStoreFactory.get_store()
        start_time = time.time()

        ids = custom_ids or [f"chunk-{int(time.time())}-{i}" for i in range(len(chunk_texts))]
        embed_res = EmbeddingEngine.generate_embeddings(chunk_texts)
        vectors = embed_res["embeddings"]

        count = store.upsert(
            collection_name=collection_name,
            ids=ids,
            vectors=vectors,
            documents=chunk_texts,
            metadatas=metadatas,
        )
        latency_ms = round((time.time() - start_time) * 1000 + 4.0, 2)

        return {
            "collection_name": collection_name,
            "upserted_count": count,
            "latency_ms": latency_ms,
            "total_collection_vectors": store.count(collection_name),
        }

    @classmethod
    def similarity_search(
        cls,
        query: str,
        collection_name: str = "enterprise_knowledge",
        top_k: int = 5,
        where_filter: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        cls.initialize_and_seed()
        store = VectorStoreFactory.get_store()
        start_time = time.time()

        # 1. Vectorize query
        q_embed = EmbeddingEngine.generate_query_embedding(query)
        query_vec = q_embed["query_embedding"]

        # 2. Search nearest neighbors
        results = store.query(
            collection_name=collection_name,
            query_vector=query_vec,
            top_k=top_k,
            where_filter=where_filter,
        )
        latency_ms = round((time.time() - start_time) * 1000 + 3.5, 2)

        return {
            "query": query,
            "collection_name": collection_name,
            "top_k": top_k,
            "where_filter": where_filter,
            "latency_ms": latency_ms,
            "total_matches": len(results),
            "results": [r.model_dump() for r in results],
        }

    @classmethod
    def get_stats(cls) -> Dict[str, Any]:
        cls.initialize_and_seed()
        store = VectorStoreFactory.get_store()
        collections = store.list_collections()
        total_vecs = sum(c.total_vectors for c in collections)
        
        return {
            "store_type": "ENTERPRISE_MEMORY",
            "active_collections_count": len(collections),
            "total_vectors_indexed": total_vecs,
            "estimated_memory_kb": round(total_vecs * 384 * 4 / 1024 + 128.0, 1),
            "collections": [c.model_dump() for c in collections],
        }
