from sqlalchemy.orm import Session
from app.models.book import Book
from app.schemas.book import BookCreate
from app.services.cache import CacheService

class BookService:
    def __init__(self, db: Session, cache: CacheService):
        self.db = db
        self.cache = cache

    def get_books(self):
        cached_books = self.cache.get("all_books")
        if cached_books:
            return cached_books
            
        books = self.db.query(Book).all()
        
        try:
            self.cache.set("all_books", books)
        except Exception as e:
            pass
            
        return books

    def create_book(self, book: BookCreate):
        db_book = Book(**book.dict())
        self.db.add(db_book)
        self.db.commit()
        self.db.refresh(db_book)
        
        try:
            self.cache.delete("all_books")
        except Exception:
            pass
            
        return db_book

    def get_book(self, book_id: int):
        return self.db.query(Book).filter(Book.id == book_id).first()