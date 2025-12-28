from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from config import settings

# 1. Create the engine (The connection pool)
engine = create_engine(settings.DATABASE_URL)

# 2. Create the SessionLocal (The factory that gives us database sessions)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 3. Create Base (The parent class for your database models)
Base = declarative_base()

# 4. Dependency (We use this in FastAPI endpoints later)
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()