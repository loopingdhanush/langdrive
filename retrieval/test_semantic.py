from database.connection import SessionLocal
from database.models import DocumentChunk
from retrieval.embeddings import EmbeddingService
from retrieval.indexer import EmbeddingIndexer
from retrieval.semantic import SemanticRetriever


def main():

    db = SessionLocal()

    try:

        embedding_service = EmbeddingService()

        chunk = (
            db.query(DocumentChunk)
            .first()
        )

        if not chunk:

            print(
                "No chunks found."
            )

            print(
                "Upload and ingest a document first."
            )

            return

        print(
            "Generating embeddings..."
        )

        indexer = EmbeddingIndexer(
            db,
            embedding_service,
        )

        count = indexer.index_file(
            chunk.file_id
        )

        print(
            f"Embedded {count} chunks."
        )

        query = input(
            "\nSearch query: "
        ).strip()

        query_embedding = (
            embedding_service.embed_query(
                query
            )
        )

        retriever = SemanticRetriever(
            db
        )

        results = retriever.search(
            query_embedding,
            limit=5,
        )

        print(
            f"\nFound {len(results)} results:\n"
        )

        for index, result in enumerate(
            results,
            start=1,
        ):

            print(
                f"--- Result {index} ---"
            )

            print(
                f"Chunk: {result.chunk_index}"
            )

            print(
                f"Page: {result.page_number}"
            )

            print(
                result.content[:500]
            )

            print()

    finally:

        db.close()


if __name__ == "__main__":
    main()