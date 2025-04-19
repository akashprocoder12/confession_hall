from pydantic import BaseModel
from typing import List, Optional

class Confession(BaseModel):
    text: str
    tags: List[str] = []

class Comment(BaseModel):
    confession_id: str
    comment: str

class Like(BaseModel):
    confession_id: str
    action: str  # Add action field
