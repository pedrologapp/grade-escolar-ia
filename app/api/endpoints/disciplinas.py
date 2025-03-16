from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
import traceback

from app.models.database import get_db
from app.models.disciplina import Disciplina
from app.schemas.disciplina import DisciplinaCreate, DisciplinaResponse, DisciplinaUpdate

router = APIRouter()

@router.get("/", response_model=List[DisciplinaResponse])
def read_disciplinas(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Recupera a lista de disciplinas."""
    try:
        disciplinas = db.query(Disciplina).offset(skip).limit(limit).all()
        return disciplinas
    except Exception as e:
        error_details = traceback.format_exc()
        print(f"Erro ao buscar disciplinas: {str(e)}")
        print(f"Detalhes do erro: {error_details}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao buscar disciplinas: {str(e)}"
        )

@router.post("/", response_model=DisciplinaResponse, status_code=status.HTTP_201_CREATED)
def create_disciplina(disciplina: DisciplinaCreate, db: Session = Depends(get_db)):
    """Cria uma nova disciplina."""
    try:
        print(f"Tentando criar disciplina: {disciplina}")
        db_disciplina = Disciplina(**disciplina.dict())
        db.add(db_disciplina)
        db.commit()
        db.refresh(db_disciplina)
        print(f"Disciplina criada com sucesso: {db_disciplina}")
        return db_disciplina
    except Exception as e:
        db.rollback()
        error_details = traceback.format_exc()
        print(f"Erro ao criar disciplina: {str(e)}")
        print(f"Detalhes do erro: {error_details}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao criar disciplina: {str(e)}"
        )

@router.get("/{disciplina_id}", response_model=DisciplinaResponse)
def read_disciplina(disciplina_id: int, db: Session = Depends(get_db)):
    """Recupera informações de uma disciplina específica."""
    try:
        disciplina = db.query(Disciplina).filter(Disciplina.id == disciplina_id).first()
        if disciplina is None:
            raise HTTPException(status_code=404, detail="Disciplina não encontrada")
        return disciplina
    except HTTPException:
        raise
    except Exception as e:
        error_details = traceback.format_exc()
        print(f"Erro ao buscar disciplina: {str(e)}")
        print(f"Detalhes do erro: {error_details}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao buscar disciplina: {str(e)}"
        )

@router.put("/{disciplina_id}", response_model=DisciplinaResponse)
def update_disciplina(disciplina_id: int, disciplina: DisciplinaUpdate, db: Session = Depends(get_db)):
    """Atualiza uma disciplina existente."""
    try:
        db_disciplina = db.query(Disciplina).filter(Disciplina.id == disciplina_id).first()
        if db_disciplina is None:
            raise HTTPException(status_code=404, detail="Disciplina não encontrada")
        
        for key, value in disciplina.dict(exclude_unset=True).items():
            setattr(db_disciplina, key, value)
        
        db.commit()
        db.refresh(db_disciplina)
        return db_disciplina
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        error_details = traceback.format_exc()
        print(f"Erro ao atualizar disciplina: {str(e)}")
        print(f"Detalhes do erro: {error_details}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao atualizar disciplina: {str(e)}"
        )

@router.delete("/{disciplina_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_disciplina(disciplina_id: int, db: Session = Depends(get_db)):
    """Remove uma disciplina."""
    try:
        disciplina = db.query(Disciplina).filter(Disciplina.id == disciplina_id).first()
        if disciplina is None:
            raise HTTPException(status_code=404, detail="Disciplina não encontrada")
        
        db.delete(disciplina)
        db.commit()
        return None
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        error_details = traceback.format_exc()
        print(f"Erro ao excluir disciplina: {str(e)}")
        print(f"Detalhes do erro: {error_details}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao excluir disciplina: {str(e)}"
        )