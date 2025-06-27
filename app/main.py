from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.database import SessionLocal, engine, Base
from app.schemas.book import Book, BookCreate
from app.schemas.review import Review, ReviewCreate
from app.services.book import BookService
from app.services.review import ReviewService
from app.services.cache import CacheService
import os

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Book Review Service",
    description="A simple service for managing books and reviews",
    version="1.0.0",
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_cache():
    return CacheService()

@app.get("/books", response_model=list[Book])
def list_books(
    db: Session = Depends(get_db),
    cache: CacheService = Depends(get_cache)
):
    book_service = BookService(db, cache)
    try:
        return book_service.get_books()
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/books", response_model=Book)
def create_book(
    book: BookCreate,
    db: Session = Depends(get_db),
    cache: CacheService = Depends(get_cache)
):
    book_service = BookService(db, cache)
    return book_service.create_book(book)

@app.get("/books/{book_id}/reviews", response_model=list[Review])
def list_reviews(
    book_id: int,
    db: Session = Depends(get_db)
):
    review_service = ReviewService(db)
    book_service = BookService(db, CacheService())
    
    if not book_service.get_book(book_id):
        raise HTTPException(status_code=404, detail="Book not found")
    
    return review_service.get_reviews_for_book(book_id)

@app.post("/books/{book_id}/reviews", response_model=Review)
def create_review(
    book_id: int,
    review: ReviewCreate,
    db: Session = Depends(get_db)
):
    review_service = ReviewService(db)
    book_service = BookService(db, CacheService())
    
    if not book_service.get_book(book_id):
        raise HTTPException(status_code=404, detail="Book not found")
    
    return review_service.create_review(book_id, review)