from dataclasses import dataclass

from ingestion.extractor import ExtractedPage


@dataclass
class DocumentChunkData:
    content: str
    page_number: int | None
    section: str | None
    chunk_index: int

def chunk_text(
    pages: list[ExtractedPage],
    chunk_size: int = 1200,
    chunk_overlap: int = 200,
) -> list[DocumentChunkData]:

    chunks = []

    chunk_index = 0

    for page in pages:

        text = page.text.strip()

        if not text:
            continue

        start = 0

        while start < len(text):

            end = start + chunk_size

            content = text[start:end].strip()

            if content:

                chunks.append(
                    DocumentChunkData(
                        content=content,
                        page_number=page.page_number,
                        section=None,
                        chunk_index=chunk_index,
                    )
                )

                chunk_index += 1

            if end >= len(text):
                break

            start = end - chunk_overlap

    return chunks