from sqlalchemy.orm import Session
from app.models.review import Review
from app.schemas.review import ReviewCreate

class ReviewService:
    def __init__(self, db: Session):
        self.db = db

    def get_reviews_for_book(self, book_id: int):
        return self.db.query(Review).filter(Review.book_id == book_id).all()

    def create_review(self, book_id: int, review: ReviewCreate):
        db_review = Review(**review.dict(), book_id=book_id)
        self.db.add(db_review)
        self.db.commit()
        self.db.refresh(db_review)
        return db_review