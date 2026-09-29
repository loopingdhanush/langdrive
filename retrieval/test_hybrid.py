from database.connection import SessionLocal
from retrieval.hybrid import HybridRetriever


def main():

    db = SessionLocal()

    try:

        retriever = HybridRetriever(db)

        query = input(
            "Search query: "
        ).strip()

        print(
            "\nRunning hybrid retrieval + reranking..."
        )

        results = retriever.search(
            query=query,
            candidate_limit=20,
            limit=5,
        )

        print(
            f"\nFinal results: {len(results)}\n"
        )

        for index, (chunk, score) in enumerate(
            results,
            start=1,
        ):

            print(
                f"--- Result {index} ---"
            )

            print(
                f"Reranker score: {score:.4f}"
            )

            print(
                f"File ID: {chunk.file_id}"
            )

            print(
                f"Page: {chunk.page_number}"
            )

            print(
                f"Chunk: {chunk.chunk_index}"
            )

            print(
                chunk.content[:500]
            )

            print()

    finally:

        db.close()


if __name__ == "__main__":
    main()