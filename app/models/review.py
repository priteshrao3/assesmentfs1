from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from app.db.database import Base

class Review(Base):
    __tablename__ = "reviews"
    
    id = Column(Integer, primary_key=True, index=True)
    book_id = Column(Integer, ForeignKey("books.id"))
    reviewer_name = Column(String)
    content = Column(String)
    rating = Column(Integer)
    
    book = relationship("Book", back_populates="reviews")