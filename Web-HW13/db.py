from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from config import settings

SQLALCHEMY_DATABASE_URL = settings.sqlalchemy_database_url
engine = create_engine(SQLALCHEMY_DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# Dependency
def get_db():
    """
    Dependency function to get a database session.

    Returns:
        sqlalchemy.orm.Session: A database session.

    Yields:
        sqlalchemy.orm.Session: A database session.

    """

    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
