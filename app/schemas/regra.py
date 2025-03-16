from pydantic import BaseModel
from typing import Optional, Dict, Any

class RegraBase(BaseModel):
    nome: str
    descricao: Optional[str] = None
    tipo: str
    condicoes: Dict[str, Any]

class RegraCreate(RegraBase):
    pass

class RegraUpdate(BaseModel):
    nome: Optional[str] = None
    descricao: Optional[str] = None
    tipo: Optional[str] = None
    condicoes: Optional[Dict[str, Any]] = None

class RegraResponse(RegraBase):
    id: int
    
    class Config:
        from_attributes = True