from database.connection import SessionLocal
from retrieval.index_manager import (
    BM25IndexManager,
)


def main():

    db = SessionLocal()

    try:

        manager = BM25IndexManager(db)

        count = manager.rebuild()

        print(
            f"Indexed {count} chunks."
        )

        if count == 0:

            print(
                "No chunks found."
            )

            return

        query = input(
            "\nSearch query: "
        ).strip()

        results = manager.search(
            query,
            limit=5,
        )

        print(
            f"\nFound {len(results)} results:\n"
        )

        for index, (chunk, score) in enumerate(
            results,
            start=1,
        ):

            print(
                f"--- Result {index} ---"
            )

            print(
                f"BM25 score: {score:.4f}"
            )

            print(
                f"Page: {chunk.page_number}"
            )

            print(
                chunk.content[:500]
            )

            print()

    finally:

        db.close()


if __name__ == "__main__":
    main()