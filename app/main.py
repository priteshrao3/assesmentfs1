from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import delete
from app.db.database import SessionLocal, engine, Base
from app.schemas.book import Book, BookCreate, BookUpdate, BookPatch
from app.schemas.review import Review, ReviewCreate, ReviewUpdate, ReviewPatch
from app.services.book import BookService
from app.services.review import ReviewService
from app.services.cache import CacheService
from app.models.book import Book as BookModel
from app.models.review import Review as ReviewModel

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Book Review Service",
    description="A service for managing books and reviews.",
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
    cache: CacheService = Depends(get_cache),
):
    book_service = BookService(db, cache)
    return book_service.get_books()


@app.get("/books/{book_id}", response_model=Book)
def get_book_by_id(
    book_id: int,
    db: Session = Depends(get_db),
    cache: CacheService = Depends(get_cache),
):
    book_service = BookService(db, cache)
    book = book_service.get_book(book_id)
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    return book


@app.post("/books", response_model=Book)
def create_book(
    book: BookCreate,
    db: Session = Depends(get_db),
    cache: CacheService = Depends(get_cache),
):
    book_service = BookService(db, cache)
    return book_service.create_book(book)


@app.put("/books/{book_id}", response_model=Book)
def update_book(
    book_id: int,
    book_data: BookUpdate,
    db: Session = Depends(get_db),
    cache: CacheService = Depends(get_cache),
):
    book_service = BookService(db, cache)
    book = book_service.get_book(book_id)
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")

    for key, value in book_data.dict().items():
        setattr(book, key, value)
    db.commit()
    db.refresh(book)

    cache.delete("all_books")

    return book


@app.patch("/books/{book_id}", response_model=Book)
def patch_book(
    book_id: int,
    book_data: BookPatch,
    db: Session = Depends(get_db),
    cache: CacheService = Depends(get_cache),
):
    book_service = BookService(db, cache)
    book = book_service.get_book(book_id)
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")

    for key, value in book_data.dict(exclude_unset=True).items():
        setattr(book, key, value)
    db.commit()
    db.refresh(book)

    cache.delete("all_books")

    return book


@app.delete("/books/{book_id}", status_code=204)
def delete_book(
    book_id: int,
    db: Session = Depends(get_db),
    cache: CacheService = Depends(get_cache),
):
    book = db.query(BookModel).filter(BookModel.id == book_id).first()
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")

    db.execute(delete(ReviewModel).where(ReviewModel.book_id == book_id))
    db.execute(delete(BookModel).where(BookModel.id == book_id))
    db.commit()

    cache.delete("all_books")

    return


@app.get("/books/{book_id}/reviews", response_model=list[Review])
def list_reviews(
    book_id: int,
    db: Session = Depends(get_db),
):
    book_service = BookService(db, CacheService())
    if not book_service.get_book(book_id):
        raise HTTPException(status_code=404, detail="Book not found")

    review_service = ReviewService(db)
    return review_service.get_reviews_for_book(book_id)


@app.post("/books/{book_id}/reviews", response_model=Review)
def create_review(
    book_id: int,
    review: ReviewCreate,
    db: Session = Depends(get_db),
):
    book_service = BookService(db, CacheService())
    if not book_service.get_book(book_id):
        raise HTTPException(status_code=404, detail="Book not found")

    review_service = ReviewService(db)
    return review_service.create_review(book_id, review)


@app.put("/books/{book_id}/reviews/{review_id}", response_model=Review)
def update_review(
    book_id: int,
    review_id: int,
    review_data: ReviewUpdate,
    db: Session = Depends(get_db),
):
    review = db.query(ReviewModel).filter(
        ReviewModel.id == review_id,
        ReviewModel.book_id == book_id
    ).first()

    if not review:
        raise HTTPException(status_code=404, detail="Review not found")

    for key, value in review_data.dict().items():
        setattr(review, key, value)

    db.commit()
    db.refresh(review)
    return review


@app.patch("/books/{book_id}/reviews/{review_id}", response_model=Review)
def patch_review(
    book_id: int,
    review_id: int,
    review_data: ReviewPatch,
    db: Session = Depends(get_db),
):
    review = db.query(ReviewModel).filter(
        ReviewModel.id == review_id,
        ReviewModel.book_id == book_id
    ).first()

    if not review:
        raise HTTPException(status_code=404, detail="Review not found")

    for key, value in review_data.dict(exclude_unset=True).items():
        setattr(review, key, value)

    db.commit()
    db.refresh(review)
    return review


@app.delete("/books/{book_id}/reviews/{review_id}", status_code=204)
def delete_review(
    book_id: int,
    review_id: int,
    db: Session = Depends(get_db),
):
    review = db.query(ReviewModel).filter(
        ReviewModel.id == review_id,
        ReviewModel.book_id == book_id
    ).first()

    if not review:
        raise HTTPException(status_code=404, detail="Review not found")

    db.delete(review)
    db.commit()
    return


@app.delete("/reset", status_code=204)
def reset_data(
    db: Session = Depends(get_db),
    cache: CacheService = Depends(get_cache)
):
    try:
        db.execute(delete(ReviewModel))
        db.execute(delete(BookModel))
        db.commit()
        try:
            cache.delete("all_books")
        except Exception:
            pass
        return
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
