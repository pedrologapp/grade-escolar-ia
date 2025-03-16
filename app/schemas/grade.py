from pydantic import BaseModel

class GradeBase(BaseModel):
    nome: str

class GradeCreate(GradeBase):
    turma_id: int  # Se precisar referenciar uma turma

class GradeResponse(GradeBase):
    id: int

    class Config:
        from_attributes = True  # Para compatibilidade com SQLAlchemy
