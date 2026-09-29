import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from database.models import DocumentChunk
from retrieval.embeddings import EmbeddingService


class EmbeddingIndexer:

    def __init__(
        self,
        db: Session,
        embedding_service: EmbeddingService,
    ):
        self.db = db
        self.embedding_service = embedding_service

    def index_file(
        self,
        file_id: uuid.UUID,
    ) -> int:

        chunks = list(
            self.db.scalars(
                select(DocumentChunk)
                .where(
                    DocumentChunk.file_id == file_id
                )
                .order_by(
                    DocumentChunk.chunk_index
                )
            ).all()
        )

        if not chunks:
            return 0

        texts = [
            chunk.content
            for chunk in chunks
        ]

        embeddings = (
            self.embedding_service.embed(texts)
        )

        for chunk, embedding in zip(
            chunks,
            embeddings,
        ):
            chunk.embedding = embedding

        self.db.commit()

        return len(chunks)