from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

# This creates a file named 'assignment.db' in your folder
SQLALCHEMY_DATABASE_URL = "sqlite:///./assignment.db"

# connect_args is needed for SQLite to allow multiple requests safely
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()