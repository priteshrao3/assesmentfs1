import pytest
from unittest.mock import MagicMock
from app.services.cache import CacheService

@pytest.fixture
def failing_cache():
    mock = MagicMock(spec=CacheService)
    mock.get.side_effect = Exception("Cache is down")
    mock.set.side_effect = Exception("Cache is down")
    return mock

def test_cache_miss_path(client, db, failing_cache):
    app.dependency_overrides[get_cache] = lambda: failing_cache
    
    from app.models import Book
    db_book = Book(title="DB Book", author="DB Author")
    db.add(db_book)
    db.commit()
    db.refresh(db_book)
    
    response = client.get("/books")
    assert response.status_code == 200
    books = response.json()
    assert len(books) == 1
    assert books[0]["title"] == "DB Book"