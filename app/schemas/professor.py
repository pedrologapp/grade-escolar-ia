from pydantic import BaseModel
from typing import List, Optional

class ProfessorBase(BaseModel):
    nome: str
    email: str
    area: Optional[str] = None

class ProfessorCreate(ProfessorBase):
    pass

class ProfessorUpdate(BaseModel):
    nome: Optional[str] = None
    email: Optional[str] = None
    area: Optional[str] = None

class ProfessorResponse(ProfessorBase):
    id: int
    
    class Config:
        from_attributes = True