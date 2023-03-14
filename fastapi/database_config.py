from sqlmodel import Session, SQLModel, create_engine

SQLLITE_DATABASE_URL = "sqlite:///./data/sql_app.db"

engine = create_engine(SQLLITE_DATABASE_URL, connect_args={
                       "check_same_thread": False})


def get_db():
    with Session(engine) as session:
        yield session


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)
