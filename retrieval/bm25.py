from rank_bm25 import BM25Okapi

from database.models import DocumentChunk


class BM25Retriever:

    def __init__(self):
        self.chunks: list[DocumentChunk] = []
        self.bm25 = None

    def build(
        self,
        chunks: list[DocumentChunk],
    ) -> None:

        self.chunks = chunks

        tokenized_documents = [
            self.tokenize(chunk.content)
            for chunk in chunks
        ]

        if not tokenized_documents:
            self.bm25 = None
            return

        self.bm25 = BM25Okapi(
            tokenized_documents
        )

    @staticmethod
    def tokenize(text: str) -> list[str]:

        return (
            text.lower()
            .replace(",", " ")
            .replace(".", " ")
            .replace(":", " ")
            .replace(";", " ")
            .replace("(", " ")
            .replace(")", " ")
            .split()
        )

    def search(
        self,
        query: str,
        limit: int = 5,
    ) -> list[tuple[DocumentChunk, float]]:

        if self.bm25 is None:
            return []

        query_tokens = self.tokenize(query)

        scores = self.bm25.get_scores(
            query_tokens
        )

        ranked_indices = sorted(
            range(len(scores)),
            key=lambda i: scores[i],
            reverse=True,
        )

        results = []

        for index in ranked_indices[:limit]:

            results.append(
                (
                    self.chunks[index],
                    float(scores[index]),
                )
            )

        return results