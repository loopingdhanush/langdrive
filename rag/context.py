from dataclasses import dataclass
from uuid import UUID

from database.models import DocumentChunk


@dataclass
class RetrievedContext:

    chunk_id: UUID

    file_id: UUID

    filename: str

    page_number: int | None

    section: str | None

    content: str

    score: float

    citation: str

class ContextBuilder:

    def build(
        self,
        results,
    ) -> list[RetrievedContext]:

        contexts = []

        for chunk, score in results:

            filename = (
                chunk.file.name
            )

            if chunk.page_number:

                citation = (
                    f"[{filename}, "
                    f"p. {chunk.page_number}]"
                )

            else:

                citation = (
                    f"[{filename}]"
                )

            contexts.append(
                RetrievedContext(
                    chunk_id=chunk.id,
                    file_id=chunk.file_id,
                    filename=filename,
                    page_number=chunk.page_number,
                    section=chunk.section,
                    content=chunk.content,
                    score=score,
                    citation=citation,
                )
            )

        return contexts

class PromptContextBuilder:

    def build(
        self,
        contexts: list[RetrievedContext],
        ) -> str:

            sections = []

            for index, context in enumerate(
                contexts,
                start=1,
            ):

                sections.append(
                    f"""
                        SOURCE {index}
                        File: {context.filename}
                        Page: {context.page_number or "N/A"}
                        Citation: {context.citation}

                        {context.content}
                        """.strip()
                )

            return "\n\n---\n\n".join(
                sections
            )