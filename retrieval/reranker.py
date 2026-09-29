from sentence_transformers import CrossEncoder


MODEL_NAME = "cross-encoder/ms-marco-MiniLM-L-6-v2"


class Reranker:

    def __init__(
        self,
        model_name: str = MODEL_NAME,
    ):
        self.model = CrossEncoder(
            model_name
        )

    def rerank(
        self,
        query: str,
        chunks,
        limit: int = 5,
    ):

        if not chunks:
            return []

        pairs = [
            (
                query,
                chunk.content,
            )
            for chunk in chunks
        ]

        scores = self.model.predict(
            pairs,
            show_progress_bar=False,
        )

        ranked = sorted(
            zip(chunks, scores),
            key=lambda item: float(item[1]),
            reverse=True,
        )

        return [
            (chunk, float(score))
            for chunk, score in ranked[:limit]
        ]