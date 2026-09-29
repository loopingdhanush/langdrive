import os
import uuid
from pathlib import Path

import streamlit as st
from dotenv import load_dotenv

from database.connection import SessionLocal
from files.manager import FileService
from storage.local import LocalStorage


load_dotenv()
def get_service():
    db = SessionLocal()

    storage_root = os.getenv(
        "STORAGE_ROOT",
        "./storage_data",
    )

    storage = LocalStorage(storage_root)

    return db, FileService(db, storage)


def init_state(service):

    if "current_folder_id" not in st.session_state:
        root = service.get_root_folder()
        st.session_state.current_folder_id = root.id

def render_sidebar(service):

    st.sidebar.title("AI Drive")

    if st.sidebar.button(
        "🏠 My Drive",
        use_container_width=True,
    ):
        root = service.get_root_folder()

        st.session_state.current_folder_id = root.id

        st.rerun()

    st.sidebar.divider()

    st.sidebar.caption("AI")

    st.sidebar.button(
        "💬 Ask AI",
        use_container_width=True,
    )

    st.sidebar.button(
        "✨ AI Overview",
        use_container_width=True,
    )


def render_breadcrumbs(service, current_folder_id):

    folder = service.get_folder(current_folder_id)

    path = []

    current = folder

    while current:
        path.append(current)
        current = current.parent

    path.reverse()

    cols = st.columns(len(path))

    for index, folder in enumerate(path):

        with cols[index]:

            if st.button(
                f"📁 {folder.name}",
                key=f"breadcrumb_{index}_{folder.id}",
                use_container_width=True,
            ):
                st.session_state.current_folder_id = (
                    folder.id
                )

                st.rerun()
def render_actions(service, current_folder_id):

    col1, col2 = st.columns([1, 1])

    with col1:

        uploaded_file = st.file_uploader(
            "Upload file",
            key="file_uploader",
        )

        if uploaded_file is not None:

            if st.button(
                "Upload",
                key="upload_button",
            ):

                temp_dir = Path(".streamlit_temp")
                temp_dir.mkdir(exist_ok=True)

                temp_path = (
                    temp_dir / uploaded_file.name
                )

                temp_path.write_bytes(
                    uploaded_file.getbuffer()
                )

                try:

                    file = service.create_file(
                        source=temp_path,
                        name=uploaded_file.name,
                        folder_id=current_folder_id,
                        mime_type=uploaded_file.type,
                    )

                    st.success(
                        f"Uploaded: {file.name}"
                    )

                finally:

                    if temp_path.exists():
                        temp_path.unlink()

                st.rerun()

    with col2:

        with st.popover("📁 New folder"):

            folder_name = st.text_input(
                "Folder name",
                key="new_folder_name",
            )

            if st.button(
                "Create",
                key="create_folder",
            ):

                try:

                    service.create_folder(
                        name=folder_name,
                        parent_id=current_folder_id,
                    )

                    st.success(
                        "Folder created"
                    )

                    st.rerun()

                except ValueError as e:

                    st.error(str(e))

def render_folders(service, current_folder_id):

    folders = service.list_folders(
        parent_id=current_folder_id
    )

    if not folders:
        return

    st.markdown("### Folders")

    columns = st.columns(4)

    for index, folder in enumerate(folders):

        with columns[index % 4]:

            if st.button(
                f"📁 {folder.name}",
                key=f"folder_{folder.id}",
                use_container_width=True,
            ):

                st.session_state.current_folder_id = (
                    folder.id
                )

                st.rerun()


def render_files(service, current_folder_id):

    if current_folder_id is None:
        return

    files = service.list_files(
        folder_id=current_folder_id
    )

    st.markdown("### Files")

    if not files:
        st.info("No files in this folder.")
        return

    for file in files:

        col1, col2, col3, col4 = st.columns(
            [5, 1, 1, 1]
        )

        with col1:
            st.write(
                f"📄 **{file.name}**"
            )

        with col2:

            file_path = service.storage.get(
                file.storage_key
            )

            with open(file_path, "rb") as f:

                st.download_button(
                    "⬇️",
                    data=f,
                    file_name=file.name,
                    key=f"download_{file.id}",
                )

        with col3:

            if st.button(
                "✏️",
                key=f"rename_{file.id}",
            ):

                st.session_state[
                    f"renaming_{file.id}"
                ] = True

        with col4:

            if st.button(
                "🗑️",
                key=f"delete_{file.id}",
            ):

                st.session_state[
                    f"confirm_delete_{file.id}"
                ] = True

        if st.session_state.get(
            f"renaming_{file.id}",
            False,
        ):

            new_name = st.text_input(
                "New name",
                value=file.name,
                key=f"rename_input_{file.id}",
            )

            if st.button(
                "Save",
                key=f"save_rename_{file.id}",
            ):

                service.rename_file(
                    file.id,
                    new_name,
                )

                st.session_state[
                    f"renaming_{file.id}"
                ] = False

                st.rerun()

        if st.session_state.get(
            f"confirm_delete_{file.id}",
            False,
        ):

            st.warning(
                f"Delete **{file.name}**?"
            )

            yes, no = st.columns(2)

            with yes:

                if st.button(
                    "Yes, delete",
                    key=f"yes_delete_{file.id}",
                ):

                    service.delete_file(file.id)

                    st.session_state[
                        f"confirm_delete_{file.id}"
                    ] = False

                    st.rerun()

            with no:

                if st.button(
                    "Cancel",
                    key=f"cancel_delete_{file.id}",
                ):

                    st.session_state[
                        f"confirm_delete_{file.id}"
                    ] = False

                    st.rerun()


def render():

    db, service = get_service()

    try:

        init_state(service)

        render_sidebar(service)

        current_folder_id = (
            st.session_state.current_folder_id
        )

        if current_folder_id is None:
            current_folder_id = service.get_root_folder().id

            st.session_state.current_folder_id = (
                current_folder_id
            )

        render_breadcrumbs(
            service,
            current_folder_id,
        )

        st.divider()

        render_actions(
            service,
            current_folder_id,
        )

        st.divider()

        render_folders(
            service,
            current_folder_id,
        )

        render_files(
            service,
            current_folder_id,
        )

    finally:

        db.close()

