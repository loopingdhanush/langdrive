from dataclasses import dataclass
from uuid import UUID


@dataclass
class RetrievalScope:

    file_id: UUID | None = None

    folder_id: UUID | None = None

    file_ids: list[UUID] | None = None

    def validate(self):

        scopes = sum([
            self.file_id is not None,
            self.folder_id is not None,
            bool(self.file_ids),
        ])

        if scopes > 1:
            raise ValueError(
                "Only one retrieval scope can be active."
            )