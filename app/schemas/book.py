from pydantic import BaseModel
from typing import List, Optional
from .review import Review

class BookBase(BaseModel):
    title: str
    author: str
    description: Optional[str] = None

class BookCreate(BookBase):
    pass

class Book(BookBase):
    id: int
    reviews: List[Review] = []
    
    class Config:
        orm_mode = True