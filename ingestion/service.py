import uuid
from pathlib import Path

from sqlalchemy import delete
from sqlalchemy.orm import Session

from database.models import DocumentChunk, File
from ingestion.chunker import chunk_text
from ingestion.extractor import extract_document
from storage.base import StorageProvider


class IngestionService:

    def __init__(
        self,
        db: Session,
        storage: StorageProvider,
    ):
        self.db = db
        self.storage = storage

    def ingest_file(
        self,
        file_id: uuid.UUID,
    ) -> int:

        file = self.db.get(File, file_id)

        if not file:
            raise FileNotFoundError(
                f"File not found: {file_id}"
            )

        path = self.storage.get(
            file.storage_key
        )

        pages = extract_document(
            path,
            file.mime_type,
        )

        chunks = chunk_text(pages)

        # Make ingestion idempotent.
        # Re-ingesting replaces old chunks.
        self.db.execute(
            delete(DocumentChunk).where(
                DocumentChunk.file_id == file.id
            )
        )

        for chunk in chunks:

            document_chunk = DocumentChunk(
                id=uuid.uuid4(),
                file_id=file.id,
                folder_id=file.folder_id,
                content=chunk.content,
                page_number=chunk.page_number,
                section=chunk.section,
                chunk_index=chunk.chunk_index,
            )

            self.db.add(document_chunk)

        self.db.commit()

        return len(chunks)