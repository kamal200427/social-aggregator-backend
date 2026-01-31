# ./database/connection.py

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from backend.models import Base

# -----------------------------
# Database URL
# -----------------------------
# Using SQLite for simplicity. 
# You can switch to PostgreSQL or MySQL by changing this URL
DATABASE_URL = "sqlite:///./social_posts.db"

# -----------------------------
# Create Engine
# -----------------------------
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False}  # Only needed for SQLite
)

# -----------------------------
# Create Session
# -----------------------------
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# -----------------------------
# Initialize DB tables
# -----------------------------
def init_db():
    """
    Create all tables in the database.
    """
    Base.metadata.create_all(bind=engine)

# -----------------------------
# Dependency helper for FastAPI
# -----------------------------
def get_db():
    """
    Dependency: Returns a SQLAlchemy DB session.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# -----------------------------
# Example usage
# -----------------------------
if __name__ == "__main__":
    init_db()
    print("Database initialized successfully.")
