from database.connection import SessionLocal
from database.models import File, DocumentChunk
from ingestion.service import IngestionService
from storage.local import LocalStorage


def main():

    db = SessionLocal()

    try:

        storage = LocalStorage(
            "./storage_data"
        )

        service = IngestionService(
            db,
            storage,
        )

        file = (
            db.query(File)
            .first()
        )

        if not file:
            print(
                "No files found. Upload a PDF first."
            )
            return

        print(
            f"Ingesting: {file.name}"
        )

        count = service.ingest_file(
            file.id
        )

        print(
            f"Created {count} chunks."
        )

        chunks = (
            db.query(DocumentChunk)
            .filter(
                DocumentChunk.file_id == file.id
            )
            .order_by(
                DocumentChunk.chunk_index
            )
            .all()
        )

        for chunk in chunks:

            print()
            print(
                f"Chunk {chunk.chunk_index}"
            )
            print(
                f"Page: {chunk.page_number}"
            )
            print(
                chunk.content[:300]
            )

    finally:

        db.close()


if __name__ == "__main__":
    main()