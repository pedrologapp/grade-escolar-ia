from fastapi import APIRouter, Depends, HTTPException, status, Body
from sqlalchemy.orm import Session
from typing import List
import traceback

from app.models.database import get_db
from app.models.turma import Turma
from app.schemas.turma import TurmaCreate, TurmaResponse, TurmaUpdate

router = APIRouter()

@router.get("/", response_model=List[TurmaResponse])
def read_turmas(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Recupera a lista de turmas."""
    try:
        turmas = db.query(Turma).offset(skip).limit(limit).all()
        return turmas
    except Exception as e:
        error_details = traceback.format_exc()
        print(f"Erro ao buscar turmas: {str(e)}")
        print(f"Detalhes do erro: {error_details}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao buscar turmas: {str(e)}"
        )

@router.post("/", response_model=TurmaResponse, status_code=status.HTTP_201_CREATED)
def create_turma(turma: TurmaCreate = Body(...), db: Session = Depends(get_db)):
    """Cria uma nova turma."""
    try:
        print(f"Tentando criar turma: {turma}")
        db_turma = Turma(**turma.model_dump())
        db.add(db_turma)
        db.commit()
        db.refresh(db_turma)
        print(f"Turma criada com sucesso: {db_turma}")
        return db_turma
    except Exception as e:
        db.rollback()
        error_details = traceback.format_exc()
        print(f"Erro ao criar turma: {str(e)}")
        print(f"Detalhes do erro: {error_details}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao criar turma: {str(e)}"
        )

@router.get("/{turma_id}", response_model=TurmaResponse)
def read_turma(turma_id: int, db: Session = Depends(get_db)):
    """Recupera informações de uma turma específica."""
    turma = db.query(Turma).filter(Turma.id == turma_id).first()
    if turma is None:
        raise HTTPException(status_code=404, detail="Turma não encontrada")
    return turma

@router.put("/{turma_id}", response_model=TurmaResponse)
def update_turma(turma_id: int, turma: TurmaUpdate, db: Session = Depends(get_db)):
    """Atualiza uma turma existente."""
    db_turma = db.query(Turma).filter(Turma.id == turma_id).first()
    if db_turma is None:
        raise HTTPException(status_code=404, detail="Turma não encontrada")
    
    for key, value in turma.model_dump(exclude_unset=True).items():
        setattr(db_turma, key, value)
    
    db.commit()
    db.refresh(db_turma)
    return db_turma

@router.delete("/{turma_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_turma(turma_id: int, db: Session = Depends(get_db)):
    """Remove uma turma."""
    turma = db.query(Turma).filter(Turma.id == turma_id).first()
    if turma is None:
        raise HTTPException(status_code=404, detail="Turma não encontrada")
    
    db.delete(turma)
    db.commit()
    return {"message": "Turma removida com sucesso"}
