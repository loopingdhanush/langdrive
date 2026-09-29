from sqlalchemy import select
from sqlalchemy.orm import Session

from database.models import DocumentChunk
from retrieval.bm25 import BM25Retriever


class BM25IndexManager:

    def __init__(self, db: Session):

        self.db = db
        self.retriever = BM25Retriever()

    def rebuild(
        self,
        file_id=None,
        folder_id=None,
        file_ids=None,
    ):

        statement = select(
            DocumentChunk
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

        chunks = list(
            self.db.scalars(
                statement
            ).all()
        )

        self.retriever.build(chunks)

        return len(chunks)

    def search(
        self,
        query: str,
        limit: int = 5,
    ):

        return self.retriever.search(
            query,
            limit,
        )