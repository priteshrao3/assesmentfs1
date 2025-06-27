from pydantic import BaseModel, ConfigDict
from typing import Optional, List
from app.schemas.review import Review

class BookBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    title: str
    author: str
    description: Optional[str] = None

class BookCreate(BookBase):
    pass

class BookUpdate(BookBase):
    pass

class BookPatch(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    title: Optional[str] = None
    author: Optional[str] = None
    description: Optional[str] = None

class Book(BookBase):
    id: int
    reviews: List[Review] = []