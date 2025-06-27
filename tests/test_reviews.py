import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.db.database import Base
from app.schemas import BookCreate, ReviewCreate

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

def test_create_and_list_reviews(client):
    book_data = {
        "title": "Test Book",
        "author": "Test Author",
        "description": "Test Description"
    }
    book_response = client.post("/books", json=book_data)
    book_id = book_response.json()["id"]
    
    review_data = {
        "reviewer_name": "Test Reviewer",
        "content": "Great book!",
        "rating": 5
    }
    response = client.post(f"/books/{book_id}/reviews", json=review_data)
    assert response.status_code == 200
    review = response.json()
    assert review["reviewer_name"] == review_data["reviewer_name"]
    assert review["book_id"] == book_id
    
    response = client.get(f"/books/{book_id}/reviews")
    assert response.status_code == 200
    reviews = response.json()
    assert len(reviews) == 1
    assert reviews[0]["id"] == review["id"]