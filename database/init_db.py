from sqlalchemy import text

from database.connection import Base, engine
from database.models import Folder, File


def init_db():
    with engine.begin() as connection:
        connection.execute(
            text("CREATE EXTENSION IF NOT EXISTS vector")
        )

    Base.metadata.create_all(engine)


if __name__ == "__main__":
    init_db()
    print("Database initialized.")