from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
import traceback

from app.models.database import get_db
from app.models.horario import Horario
from app.schemas.horario import HorarioCreate, HorarioResponse, HorarioUpdate

router = APIRouter()

@router.get("/", response_model=List[HorarioResponse])
def read_horarios(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Recupera a lista de horários."""
    try:
        horarios = db.query(Horario).offset(skip).limit(limit).all()
        return horarios
    except Exception as e:
        error_details = traceback.format_exc()
        print(f"Erro ao buscar horários: {str(e)}")
        print(f"Detalhes do erro: {error_details}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao buscar horários: {str(e)}"
        )

@router.post("/", response_model=HorarioResponse, status_code=status.HTTP_201_CREATED)
def create_horario(horario: HorarioCreate, db: Session = Depends(get_db)):
    """Cria um novo horário."""
    try:
        print(f"Tentando criar horário: {horario}")
        db_horario = Horario(**horario.dict())
        db.add(db_horario)
        db.commit()
        db.refresh(db_horario)
        print(f"Horário criado com sucesso: {db_horario}")
        return db_horario
    except Exception as e:
        db.rollback()
        error_details = traceback.format_exc()
        print(f"Erro ao criar horário: {str(e)}")
        print(f"Detalhes do erro: {error_details}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao criar horário: {str(e)}"
        )

@router.get("/{horario_id}", response_model=HorarioResponse)
def read_horario(horario_id: int, db: Session = Depends(get_db)):
    """Recupera informações de um horário específico."""
    try:
        horario = db.query(Horario).filter(Horario.id == horario_id).first()
        if horario is None:
            raise HTTPException(status_code=404, detail="Horário não encontrado")
        return horario
    except HTTPException:
        raise
    except Exception as e:
        error_details = traceback.format_exc()
        print(f"Erro ao buscar horário: {str(e)}")
        print(f"Detalhes do erro: {error_details}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao buscar horário: {str(e)}"
        )

@router.put("/{horario_id}", response_model=HorarioResponse)
def update_horario(horario_id: int, horario: HorarioUpdate, db: Session = Depends(get_db)):
    """Atualiza um horário existente."""
    try:
        db_horario = db.query(Horario).filter(Horario.id == horario_id).first()
        if db_horario is None:
            raise HTTPException(status_code=404, detail="Horário não encontrado")
        
        for key, value in horario.dict(exclude_unset=True).items():
            setattr(db_horario, key, value)
        
        db.commit()
        db.refresh(db_horario)
        return db_horario
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        error_details = traceback.format_exc()
        print(f"Erro ao atualizar horário: {str(e)}")
        print(f"Detalhes do erro: {error_details}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao atualizar horário: {str(e)}"
        )

@router.delete("/{horario_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_horario(horario_id: int, db: Session = Depends(get_db)):
    """Remove um horário."""
    try:
        horario = db.query(Horario).filter(Horario.id == horario_id).first()
        if horario is None:
            raise HTTPException(status_code=404, detail="Horário não encontrado")
        
        db.delete(horario)
        db.commit()
        return None
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        error_details = traceback.format_exc()
        print(f"Erro ao excluir horário: {str(e)}")
        print(f"Detalhes do erro: {error_details}")