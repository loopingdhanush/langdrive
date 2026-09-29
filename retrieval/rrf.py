from collections import defaultdict


def reciprocal_rank_fusion(
    ranked_lists,
    k: int = 60,
    limit: int = 10,
):
    scores = defaultdict(float)

    chunks = {}

    for results in ranked_lists:

        for rank, chunk in enumerate(
            results,
            start=1,
        ):

            chunk_id = chunk.id

            scores[chunk_id] += (
                1 / (k + rank)
            )

            chunks[chunk_id] = chunk

    ranked = sorted(
        scores.items(),
        key=lambda item: item[1],
        reverse=True,
    )

    return [
        (
            chunks[chunk_id],
            score,
        )
        for chunk_id, score in ranked[:limit]
    ]