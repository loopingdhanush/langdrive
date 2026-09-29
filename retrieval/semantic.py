from sqlalchemy import select
from sqlalchemy.orm import Session

from database.models import DocumentChunk


class SemanticRetriever:

    def __init__(self, db: Session):
        self.db = db

    def search(
        self,
        query_embedding: list[float],
        limit: int = 5,
        file_id=None,
        folder_id=None,
        file_ids=None,
    ):

        statement = select(
            DocumentChunk
        ).where(
            DocumentChunk.embedding.is_not(None)
        )

        if file_id is not None:

            statement = statement.where(
                DocumentChunk.file_id == file_id
            )

        elif folder_id is not None:

            statement = statement.where(
                DocumentChunk.folder_id == folder_id
            )

        elif file_ids:

            statement = statement.where(
                DocumentChunk.file_id.in_(file_ids)
            )

        statement = (
            statement
            .order_by(
                DocumentChunk.embedding.cosine_distance(
                    query_embedding
                )
            )
            .limit(limit)
        )

        return list(
            self.db.scalars(statement).all()
        )