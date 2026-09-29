from dataclasses import dataclass
from pathlib import Path

import fitz


@dataclass
class ExtractedPage:
    text: str
    page_number: int | None = None


def extract_pdf(path: Path) -> list[ExtractedPage]:

    pages = []

    document = fitz.open(path)

    try:

        for page_number, page in enumerate(
            document,
            start=1,
        ):

            text = page.get_text("text").strip()

            if not text:
                continue

            pages.append(
                ExtractedPage(
                    text=text,
                    page_number=page_number,
                )
            )

    finally:
        document.close()

    return pages


def extract_text(path: Path) -> list[ExtractedPage]:

    text = path.read_text(
        encoding="utf-8",
        errors="ignore",
    ).strip()

    if not text:
        return []

    return [
        ExtractedPage(
            text=text,
            page_number=None,
        )
    ]


def extract_document(
    path: Path,
    mime_type: str | None = None,
) -> list[ExtractedPage]:

    suffix = path.suffix.lower()

    if suffix == ".pdf" or mime_type == "application/pdf":
        return extract_pdf(path)

    if suffix in {".txt", ".md"}:
        return extract_text(path)

    raise ValueError(
        f"Unsupported document type: {suffix}"
    )