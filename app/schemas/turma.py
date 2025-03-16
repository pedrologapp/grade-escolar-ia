from pydantic import BaseModel
from typing import Optional

class TurmaBase(BaseModel):
    codigo: str
    periodo: str
    disciplina_id: int

class TurmaCreate(TurmaBase):
    class Config:
        schema_extra = {
            "example": {
                "codigo": "TURMA-001",
                "periodo": "2024.1",
                "disciplina_id": 1
            }
        }

class TurmaUpdate(BaseModel):
    codigo: Optional[str] = None
    periodo: Optional[str] = None
    disciplina_id: Optional[int] = None

class TurmaResponse(TurmaBase):
    id: int
    
    class Config:
        from_attributes = True
