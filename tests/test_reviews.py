def test_create_and_list_reviews(client, db):
    book_data = {
        "title": "Test Book",
        "author": "Test Author",
        "description": "Test Description"
    }
    book_response = client.post("/books", json=book_data)
    book_id = book_response.json()["id"]
    
    response = client.get(f"/books/{book_id}/reviews")
    assert response.status_code == 200
    assert len(response.json()) == 0
    
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