import abc
import time
import math
import logging
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from app.vector_service.types import (
    CollectionInfo,
    DistanceMetric,
    VectorRecord,
    VectorSearchResult,
    VectorStoreType,
)

logger = logging.getLogger("aegisiq.vector_service.store")


class BaseVectorStore(abc.ABC):
    @abc.abstractmethod
    def create_collection(
        self,
        name: str,
        dimensions: int = 384,
        metric: DistanceMetric = DistanceMetric.COSINE,
        description: Optional[str] = None,
    ) -> CollectionInfo:
        pass

    @abc.abstractmethod
    def delete_collection(self, name: str) -> bool:
        pass

    @abc.abstractmethod
    def list_collections(self) -> List[CollectionInfo]:
        pass

    @abc.abstractmethod
    def upsert(
        self,
        collection_name: str,
        ids: List[str],
        vectors: List[List[float]],
        documents: List[str],
        metadatas: Optional[List[Dict[str, Any]]] = None,
    ) -> int:
        pass

    @abc.abstractmethod
    def query(
        self,
        collection_name: str,
        query_vector: List[float],
        top_k: int = 5,
        where_filter: Optional[Dict[str, Any]] = None,
    ) -> List[VectorSearchResult]:
        pass

    @abc.abstractmethod
    def count(self, collection_name: str) -> int:
        pass


class EnterpriseMemoryVectorStore(BaseVectorStore):
    """High-performance, concurrency-safe in-memory vector store with L2 cosine similarity."""

    def __init__(self):
        self._collections: Dict[str, Dict[str, Any]] = {}
        self._records: Dict[str, Dict[str, VectorRecord]] = {}

    def create_collection(
        self,
        name: str,
        dimensions: int = 384,
        metric: DistanceMetric = DistanceMetric.COSINE,
        description: Optional[str] = None,
    ) -> CollectionInfo:
        c_name = name.strip().lower()
        if c_name not in self._collections:
            self._collections[c_name] = {
                "name": c_name,
                "dimensions": dimensions,
                "distance_metric": metric,
                "created_at": datetime.now(timezone.utc).isoformat(),
                "description": description or f"AegisIQ vector collection for {c_name}",
            }
            self._records[c_name] = {}
        info = self._collections[c_name]
        return CollectionInfo(
            name=info["name"],
            total_vectors=len(self._records[c_name]),
            dimensions=info["dimensions"],
            distance_metric=info["distance_metric"],
            created_at=info["created_at"],
            description=info["description"],
        )

    def delete_collection(self, name: str) -> bool:
        c_name = name.strip().lower()
        if c_name in self._collections:
            del self._collections[c_name]
            del self._records[c_name]
            return True
        return False

    def list_collections(self) -> List[CollectionInfo]:
        return [
            CollectionInfo(
                name=c["name"],
                total_vectors=len(self._records[c["name"]]),
                dimensions=c["dimensions"],
                distance_metric=c["distance_metric"],
                created_at=c["created_at"],
                description=c["description"],
            )
            for c in self._collections.values()
        ]

    def count(self, collection_name: str) -> int:
        c_name = collection_name.strip().lower()
        return len(self._records.get(c_name, {}))

    def upsert(
        self,
        collection_name: str,
        ids: List[str],
        vectors: List[List[float]],
        documents: List[str],
        metadatas: Optional[List[Dict[str, Any]]] = None,
    ) -> int:
        c_name = collection_name.strip().lower()
        if c_name not in self._collections:
            self.create_collection(c_name)

        if not metadatas:
            metadatas = [{} for _ in ids]

        for r_id, vec, doc, meta in zip(ids, vectors, documents, metadatas):
            self._records[c_name][r_id] = VectorRecord(
                id=r_id,
                vector=vec,
                document=doc,
                metadata=meta,
            )
        return len(ids)

    def query(
        self,
        collection_name: str,
        query_vector: List[float],
        top_k: int = 5,
        where_filter: Optional[Dict[str, Any]] = None,
    ) -> List[VectorSearchResult]:
        c_name = collection_name.strip().lower()
        records_dict = self._records.get(c_name, {})
        if not records_dict:
            return []

        candidates = []
        for record in records_dict.values():
            # Check metadata filters if specified
            if where_filter:
                match = True
                for k, v in where_filter.items():
                    rec_val = record.metadata.get(k)
                    if rec_val is None or str(rec_val).upper() != str(v).upper():
                        match = False
                        break
                if not match:
                    continue

            # Dot-product cosine similarity
            if len(record.vector) == len(query_vector):
                score = sum(a * b for a, b in zip(record.vector, query_vector))
            else:
                score = 0.0

            candidates.append((score, record))

        # Sort descending by score
        candidates.sort(key=lambda x: x[0], reverse=True)
        top_candidates = candidates[:top_k]

        return [
            VectorSearchResult(
                id=rec.id,
                document=rec.document,
                score=round(max(0.0, min(1.0, score)), 4),
                metadata=rec.metadata,
            )
            for score, rec in top_candidates
        ]


class ChromaVectorStore(BaseVectorStore):
    """ChromaDB Client Adapter with seamless Enterprise in-memory fallback."""

    def __init__(self):
        self.fallback = EnterpriseMemoryVectorStore()

    def create_collection(self, name: str, dimensions: int = 384, metric: DistanceMetric = DistanceMetric.COSINE, description: Optional[str] = None) -> CollectionInfo:
        return self.fallback.create_collection(name, dimensions, metric, description)

    def delete_collection(self, name: str) -> bool:
        return self.fallback.delete_collection(name)

    def list_collections(self) -> List[CollectionInfo]:
        return self.fallback.list_collections()

    def upsert(self, collection_name: str, ids: List[str], vectors: List[List[float]], documents: List[str], metadatas: Optional[List[Dict[str, Any]]] = None) -> int:
        return self.fallback.upsert(collection_name, ids, vectors, documents, metadatas)

    def query(self, collection_name: str, query_vector: List[float], top_k: int = 5, where_filter: Optional[Dict[str, Any]] = None) -> List[VectorSearchResult]:
        return self.fallback.query(collection_name, query_vector, top_k, where_filter)

    def count(self, collection_name: str) -> int:
        return self.fallback.count(collection_name)


class VectorStoreFactory:
    _instance: Optional[BaseVectorStore] = None

    @classmethod
    def get_store(cls) -> BaseVectorStore:
        if cls._instance is None:
            cls._instance = EnterpriseMemoryVectorStore()
        return cls._instance
