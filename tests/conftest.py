import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.db.database import Base, get_db
from app.models.book import Book as BookModel
from app.models.review import Review as ReviewModel
from typing import Any

SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

@pytest.fixture(scope="session")
def engine():
    engine = create_engine(
        SQLALCHEMY_DATABASE_URL,
        connect_args={"check_same_thread": False}
    )
    Base.metadata.create_all(bind=engine)
    yield engine
    Base.metadata.drop_all(bind=engine)

@pytest.fixture
def db(engine):
    connection = engine.connect()
    db = sessionmaker(bind=connection)()

    print("\nCleaning database...")
    for table in reversed(Base.metadata.sorted_tables):
        print(f"Deleting from {table}")
        db.execute(table.delete())
    db.commit()

    try:
        yield db
    finally:
        connection.close()

@pytest.fixture
def client(db):
    def override_get_db():
        try:
            yield db
            db.commit()
        except Exception:
            db.rollback()
            raise
        finally:
            pass
    
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client

@pytest.fixture
def mock_cache():
    class MockCacheService:
        def __init__(self):
            self.cache = {}
        
        def get(self, key: str):
            return self.cache.get(key)
        
        def set(self, key: str, value: Any, ttl: int = 3600):
            self.cache[key] = value
        
        def delete(self, key: str):
            self.cache.pop(key, None)
    
    return MockCacheService()