from pydantic import BaseModel
from typing import Optional
from datetime import time

class HorarioBase(BaseModel):
    dia_semana: str
    hora_inicio: time
    hora_fim: time
    sala: Optional[str] = None
    professor_id: int
    turma_id: int

class HorarioCreate(HorarioBase):
    pass

class HorarioUpdate(BaseModel):
    dia_semana: Optional[str] = None
    hora_inicio: Optional[time] = None
    hora_fim: Optional[time] = None
    sala: Optional[str] = None
    professor_id: Optional[int] = None
    turma_id: Optional[int] = None

class HorarioResponse(HorarioBase):
    id: int
    
    class Config:
        from_attributes = True