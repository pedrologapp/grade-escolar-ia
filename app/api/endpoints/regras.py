from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
import traceback

from app.models.database import get_db
from app.models.regra import Regra
from app.schemas.regra import RegraCreate, RegraResponse, RegraUpdate

router = APIRouter()

@router.get("/", response_model=List[RegraResponse])
def read_regras(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Recupera a lista de regras."""
    try:
        regras = db.query(Regra).offset(skip).limit(limit).all()
        return regras
    except Exception as e:
        error_details = traceback.format_exc()
        print(f"Erro ao buscar regras: {str(e)}")
        print(f"Detalhes do erro: {error_details}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao buscar regras: {str(e)}"
        )

@router.post("/", response_model=RegraResponse, status_code=status.HTTP_201_CREATED)
def create_regra(regra: RegraCreate, db: Session = Depends(get_db)):
    """Cria uma nova regra."""
    try:
        print(f"Tentando criar regra: {regra}")
        db_regra = Regra(**regra.dict())
        db.add(db_regra)
        db.commit()
        db.refresh(db_regra)
        print(f"Regra criada com sucesso: {db_regra}")
        return db_regra
    except Exception as e:
        db.rollback()
        error_details = traceback.format_exc()
        print(f"Erro ao criar regra: {str(e)}")
        print(f"Detalhes do erro: {error_details}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao criar regra: {str(e)}"
        )

@router.get("/{regra_id}", response_model=RegraResponse)
def read_regra(regra_id: int, db: Session = Depends(get_db)):
    """Recupera informações de uma regra específica."""
    try:
        regra = db.query(Regra).filter(Regra.id == regra_id).first()
        if regra is None:
            raise HTTPException(status_code=404, detail="Regra não encontrada")
        return regra
    except HTTPException:
        raise
    except Exception as e:
        error_details = traceback.format_exc()
        print(f"Erro ao buscar regra: {str(e)}")
        print(f"Detalhes do erro: {error_details}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao buscar regra: {str(e)}"
        )

@router.put("/{regra_id}", response_model=RegraResponse)
def update_regra(regra_id: int, regra: RegraUpdate, db: Session = Depends(get_db)):
    """Atualiza uma regra existente."""
    db_regra = db.query(Regra).filter(Regra.id == regra_id).first()
    if db_regra is None:
        raise HTTPException(status_code=404, detail="Regra não encontrada")
    
    for key, value in regra.dict(exclude_unset=True).items():
        setattr(db_regra, key, value)
    
    db.commit()
    db.refresh(db_regra)
    return db_regra

@router.delete("/{regra_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_regra(regra_id: int, db: Session = Depends(get_db)):
    """Remove uma regra."""
    regra = db.query(Regra).filter(Regra.id == regra_id).first()
    if regra is None:
        raise HTTPException(status_code=404, detail="Regra não encontrada")
    
    db.delete(regra)
    db.commit()
    return None