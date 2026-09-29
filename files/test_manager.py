from pathlib import Path

from database.connection import SessionLocal
from storage.local import LocalStorage
from files.manager import FileService


def main():
    db = SessionLocal()

    try:
        storage = LocalStorage("./storage_data")
        service = FileService(db, storage)

        # Find root
        root = service.list_folders(parent_id=None)[0]

        print("Root:", root.name, root.id)

        # Create folder
        test_folder = service.create_folder(
            name="Test Documents",
            parent_id=root.id,
        )

        print("Created folder:", test_folder.name)

        # Create temporary file
        source = Path("test.txt")
        source.write_text(
            "Hello from AI Drive!",
            encoding="utf-8",
        )

        # Upload
        file = service.create_file(
            source=source,
            name=source.name,
            folder_id=test_folder.id,
            mime_type="text/plain",
        )

        print("Uploaded:", file.name)
        print("Storage key:", file.storage_key)
        print("Size:", file.size)

        # Verify
        stored_path = storage.get(file.storage_key)

        print("Stored at:", stored_path)
        print("Content:", stored_path.read_text(encoding="utf-8"))

        # Cleanup
        source.unlink()

        service.delete_file(file.id)

        print("File deleted.")

    finally:
        db.close()


if __name__ == "__main__":
    main()