import mimetypes
import os
import uuid
from pathlib import Path

from database.connection import SessionLocal
from database.models import File, Folder


def seed():
    db = SessionLocal()

    try:
        root = db.query(Folder).filter(
            Folder.parent_id.is_(None)
        ).first()

        if not root:
            root = Folder(
                name="My Drive",
                parent_id=None,
            )
            db.add(root)
            db.flush()
            print(f"Created root folder: {root.id}")
        else:
            print("Root folder already exists.")

        storage_root = Path(os.getenv("STORAGE_ROOT", "./storage_data"))
        existing_ids = {file_id for (file_id,) in db.query(File.id).all()}
        recovered_count = 0

        for file_path in (storage_root / "files").glob("*/*"):
            if not file_path.is_file():
                continue

            try:
                file_id = uuid.UUID(file_path.parent.name)
            except ValueError:
                continue

            if file_id in existing_ids:
                continue

            storage_key = file_path.relative_to(storage_root).as_posix()
            db.add(
                File(
                    id=file_id,
                    name=file_path.name,
                    folder_id=root.id,
                    storage_key=storage_key,
                    mime_type=mimetypes.guess_type(file_path.name)[0],
                    size=file_path.stat().st_size,
                )
            )
            existing_ids.add(file_id)
            recovered_count += 1

        db.commit()
        print(f"Registered {recovered_count} stored file(s) in My Drive.")

    finally:
        db.close()


if __name__ == "__main__":
    seed()