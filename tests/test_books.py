from fastapi.testclient import TestClient
from app.main import app
from app.dependencies import get_cache

def test_create_book(client, mock_cache):
    client.delete("/reset")
    app.dependency_overrides[get_cache] = lambda: mock_cache

    response = client.get("/books")
    assert response.status_code == 200
    assert response.json() == []

    book_data = {
        "title": "Test Book",
        "author": "Test Author",
        "description": "Test Description"
    }
    response = client.post("/books", json=book_data)
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == book_data["title"]
    assert "id" in data


def test_list_books(client, mock_cache):
    client.delete("/reset")
    app.dependency_overrides[get_cache] = lambda: mock_cache

    response = client.get("/books")
    assert response.status_code == 200
    assert response.json() == [] 
    
    book_data = {
        "title": "Test Book",
        "author": "Test Author",
        "description": "Test Description"
    }
    response = client.post("/books", json=book_data)
    assert response.status_code == 200
    
    response = client.get("/books")
    assert response.status_code == 200
    books = response.json()
    assert len(books) == 1
    assert books[0]["title"] == book_data["title"]
