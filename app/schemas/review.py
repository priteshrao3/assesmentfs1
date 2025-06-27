from pydantic import BaseModel, Field

class ReviewBase(BaseModel):
    reviewer_name: str
    content: str
    rating: int = Field(..., gt=0, le=5)

class ReviewCreate(ReviewBase):
    pass

class Review(ReviewBase):
    id: int
    book_id: int
    
    class Config:
        orm_mode = True