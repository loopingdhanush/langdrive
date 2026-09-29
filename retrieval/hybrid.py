from retrieval.embeddings import EmbeddingService
from retrieval.semantic import SemanticRetriever
from retrieval.index_manager import BM25IndexManager
from retrieval.rrf import reciprocal_rank_fusion
from retrieval.reranker import Reranker


class HybridRetriever:

    def __init__(self, db):

        self.db = db

        self.embedding_service = (
            EmbeddingService()
        )

        self.semantic = SemanticRetriever(db)

        self.bm25 = BM25IndexManager(db)

        self.reranker = Reranker()

    def search(
        self,
        query: str,
        limit: int = 5,
        candidate_limit: int = 20,
        file_id=None,
        folder_id=None,
        file_ids=None,
    ):

        # -------------------------
        # Semantic
        # -------------------------

        query_embedding = (
            self.embedding_service
            .embed_query(query)
        )

        semantic_results = (
            self.semantic.search(
                query_embedding=query_embedding,
                limit=candidate_limit,
                file_id=file_id,
                folder_id=folder_id,
                file_ids=file_ids,
            )
        )

        # -------------------------
        # BM25
        # -------------------------

        self.bm25.rebuild(
            file_id=file_id,
            folder_id=folder_id,
            file_ids=file_ids,
        )

        bm25_results = self.bm25.search(
            query,
            limit=candidate_limit,
        )

        bm25_chunks = [
            chunk
            for chunk, score in bm25_results
        ]

        # -------------------------
        # RRF
        # -------------------------

        rrf_results = (
            reciprocal_rank_fusion(
                [
                    semantic_results,
                    bm25_chunks,
                ],
                limit=candidate_limit,
            )
        )

        candidates = [
            chunk
            for chunk, score in rrf_results
        ]

        # -------------------------
        # Reranking
        # -------------------------

        return self.reranker.rerank(
            query=query,
            chunks=candidates,
            limit=limit,
        )