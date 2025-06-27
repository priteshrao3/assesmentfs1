import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.db.database import Base
from app.schemas import BookCreate

SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)

@pytest.fixture
def db():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

@pytest.fixture
def client(db):
    def override_get_db():
        try:
            yield db
        finally:
            db.close()
    
    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)

class MockCacheService:
    def __init__(self):
        self.cache = {}
    
    def get(self, key: str):
        return self.cache.get(key)
    
    def set(self, key: str, value: Any, ttl: int = 3600):
        self.cache[key] = value
    
    def delete(self, key: str):
        if key in self.cache:
            del self.cache[key]

@pytest.fixture
def mock_cache():
    return MockCacheService()

def test_create_book(client, mock_cache):
    app.dependency_overrides[get_cache] = lambda: mock_cache
    
    book_data = {
        "title": "Test Book",
        "author": "Test Author",
        "description": "Test Description"
    }
    response = client.post("/books", json=book_data)
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == book_data["title"]
    assert data["author"] == book_data["author"]
    assert "id" in data

def test_list_books(client, mock_cache):
    app.dependency_overrides[get_cache] = lambda: mock_cache
    
    response = client.get("/books")
    assert response.status_code == 200
    assert len(response.json()) == 0
    
    book_data = {
        "title": "Test Book",
        "author": "Test Author",
        "description": "Test Description"
    }
    client.post("/books", json=book_data)
    
    response = client.get("/books")
    assert len(response.json()) == 1
    
    response = client.get("/books")
    assert len(response.json()) == 1