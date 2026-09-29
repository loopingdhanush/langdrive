import uuid
from pathlib import Path

from sqlalchemy import select
from sqlalchemy.orm import Session

from database.models import File, Folder
from storage.base import StorageProvider


class FileService:
    def __init__(self, db: Session, storage: StorageProvider):
        self.db = db
        self.storage = storage

    # -------------------------
    # FOLDERS
    # -------------------------

    def create_folder(
        self,
        name: str,
        parent_id: uuid.UUID | None = None,
    ) -> Folder:

        name = name.strip()

        if not name:
            raise ValueError("Folder name cannot be empty")

        if parent_id:
            parent = self.db.get(Folder, parent_id)

            if not parent:
                raise ValueError("Parent folder not found")

        folder = Folder(
            name=name,
            parent_id=parent_id,
        )

        self.db.add(folder)
        self.db.commit()
        self.db.refresh(folder)

        return folder

    def list_folders(
        self,
        parent_id: uuid.UUID | None = None,
    ) -> list[Folder]:

        statement = (
            select(Folder)
            .where(Folder.parent_id == parent_id)
            .order_by(Folder.name)
        )

        return list(self.db.scalars(statement).all())

    # -------------------------
    # FILES
    # -------------------------

    def create_file(
        self,
        source: Path,
        name: str,
        folder_id: uuid.UUID | None = None,
        mime_type: str | None = None,
    ) -> File:

        if not source.exists():
            raise FileNotFoundError(source)

        if folder_id:
            folder = self.db.get(Folder, folder_id)

            if not folder:
                raise ValueError("Folder not found")
        else:
            raise ValueError("folder_id is required")

        file_id = uuid.uuid4()

        # Physical storage key.
        # Do NOT use the user's folder path here.
        storage_key = f"files/{file_id}/{name}"

        self.storage.save(source, storage_key)

        file = File(
            id=file_id,
            name=name,
            folder_id=folder_id,
            storage_key=storage_key,
            mime_type=mime_type,
            size=source.stat().st_size,
        )

        self.db.add(file)
        self.db.commit()
        self.db.refresh(file)

        return file

    def list_files(
        self,
        folder_id: uuid.UUID,
    ) -> list[File]:

        statement = (
            select(File)
            .where(File.folder_id == folder_id)
            .order_by(File.name)
        )

        return list(self.db.scalars(statement).all())

    def get_file(self, file_id: uuid.UUID) -> File:

        file = self.db.get(File, file_id)

        if not file:
            raise FileNotFoundError(f"File not found: {file_id}")

        return file

    def rename_file(
        self,
        file_id: uuid.UUID,
        new_name: str,
        ) -> File:

        new_name = new_name.strip()

        if not new_name:
            raise ValueError("File name cannot be empty")

        file = self.get_file(file_id)

        old_storage_key = file.storage_key

        # Keep the physical file identified by UUID.
        # Only the metadata name changes.
        file.name = new_name

        self.db.commit()
        self.db.refresh(file)

        return file
    # -------------------------
    # DELETE
    # -------------------------

    def delete_file(self, file_id: uuid.UUID) -> None:

        file = self.get_file(file_id)

        self.storage.delete(file.storage_key)

        self.db.delete(file)
        self.db.commit()

    def move_file(
        self,
        file_id: uuid.UUID,
        destination_folder_id: uuid.UUID,
    ) -> File:

        file = self.get_file(file_id)

        destination = self.db.get(
            Folder,
            destination_folder_id,
        )

        if not destination:
            raise ValueError("Destination folder not found")

        file.folder_id = destination_folder_id

        self.db.commit()
        self.db.refresh(file)

        return file

    def copy_file(
        self,
        file_id: uuid.UUID,
        destination_folder_id: uuid.UUID,
        new_name: str | None = None,
    ) -> File:

        original = self.get_file(file_id)

        destination = self.db.get(
            Folder,
            destination_folder_id,
        )

        if not destination:
            raise ValueError("Destination folder not found")

        new_file_id = uuid.uuid4()

        name = new_name or original.name

        storage_key = f"files/{new_file_id}/{name}"

        source_path = self.storage.get(
            original.storage_key
        )

        self.storage.save(
            source_path,
            storage_key,
        )

        copied_file = File(
            id=new_file_id,
            name=name,
            folder_id=destination_folder_id,
            storage_key=storage_key,
            mime_type=original.mime_type,
            size=original.size,
            content_hash=original.content_hash,
        )

        self.db.add(copied_file)
        self.db.commit()
        self.db.refresh(copied_file)

        return copied_file

    def get_folder(
        self,
        folder_id: uuid.UUID,
    ) -> Folder:

        folder = self.db.get(Folder, folder_id)

        if not folder:
            raise FileNotFoundError(
                f"Folder not found: {folder_id}"
            )

        return folder

    def delete_folder(
        self,
        folder_id: uuid.UUID,
    ) -> None:

        folder = self.get_folder(folder_id)

        if folder.parent_id is None:
            raise ValueError("Cannot delete root folder")

        files = list(folder.files)

        for file in files:
            self.storage.delete(file.storage_key)

        self.db.delete(folder)
        self.db.commit()

    def get_folder_path(
        self,
        folder_id: uuid.UUID,
    ) -> str:

        folder = self.get_folder(folder_id)

        parts = []

        current = folder

        while current:
            parts.append(current.name)
            current = current.parent

        parts.reverse()

        return "/".join(parts)

    def get_file_path(
        self,
        file_id: uuid.UUID,
    ) -> str:

        file = self.get_file(file_id)

        folder_path = self.get_folder_path(
            file.folder_id
        )

        return f"{folder_path}/{file.name}"

    def get_root_folder(self) -> Folder:

        statement = (
            select(Folder)
            .where(Folder.parent_id.is_(None))
            .limit(1)
        )

        folder = self.db.scalars(statement).first()

        if not folder:
            raise FileNotFoundError(
                "Root folder does not exist"
            )

        return folder
