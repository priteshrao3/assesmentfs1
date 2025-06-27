from pydantic import BaseModel, ConfigDict
from typing import Optional

class ReviewBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    reviewer_name: str
    content: str
    rating: int

class ReviewCreate(ReviewBase):
    pass

class ReviewUpdate(ReviewBase):
    pass

class ReviewPatch(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    reviewer_name: Optional[str] = None
    content: Optional[str] = None
    rating: Optional[int] = None

class Review(ReviewBase):
    id: int
    book_id: int