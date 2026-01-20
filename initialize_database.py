import os
import pathlib

from dotenv import load_dotenv
from sqlmodel import Session, SQLModel, create_engine, select, text

from .dependencies import hash_password
from .models.asset import Asset
from .models.asset_type import AssetType
from .models.user import User, UserRole

# Should be initialized to an actual value in initialize_database(). It is then accessible in other scripts via get_engine()
engine = None


def initialize_database():
    load_dotenv()

    DATABASE_SYSTEM = os.environ.get("DATABASE_SYSTEM")
    DATABASE_FILENAME = os.environ.get("DATABASE_FILENAME")
    ADMIN_USERNAME = os.environ.get("ADMIN_USERNAME")
    ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD")

    USER_USERNAME = os.environ.get("USER_USERNAME")
    USER_PASSWORD = os.environ.get("USER_PASSWORD")

    if DATABASE_SYSTEM == "sqlite":
        engine_url = f"sqlite:///{pathlib.Path(__file__).parent}/{DATABASE_FILENAME}"
    else:
        raise NotImplementedError("Requested DATABASE_SYSTEM is not implemented.")

    global engine
    engine = create_engine(
        engine_url, echo=True, connect_args={"check_same_thread": False}
    )

    if DATABASE_SYSTEM == "sqlite":
        # The following is needed for sqlite to enforce foreign keys pointing to existing data
        with Session(engine) as session:
            # pyright error for the below line is a FastAPI bug: https://github.com/fastapi/sqlmodel/issues/376
            session.exec(text("PRAGMA foreign_keys = 1"))
            session.commit()

    SQLModel.metadata.create_all(engine)
    with engine.connect() as connection:
        connection.execute(text("PRAGMA foreign_keys=ON"))
        connection.commit()

    with Session(engine) as session:
        admin = session.exec(
            select(User).where(User.username == ADMIN_USERNAME)
        ).first()
        if not admin:
            session.add(
                User.model_validate(
                    {
                        "username": ADMIN_USERNAME,
                        "hashed_password": hash_password(str(ADMIN_PASSWORD)),
                        "role": UserRole.ADMIN,
                    }
                )
            )

        user = session.exec(select(User).where(User.username == USER_USERNAME)).first()
        if not user:
            session.add(
                User.model_validate(
                    {
                        "username": USER_USERNAME,
                        "hashed_password": hash_password(str(USER_PASSWORD)),
                        "role": UserRole.USER,
                    }
                )
            )
        session.commit()


def get_engine():
    if engine == None:
        raise Exception("Database engine was not initialized")
    return engine
