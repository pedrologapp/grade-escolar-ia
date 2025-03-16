from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.models.database import get_db
from app.models.professor import Professor
from app.schemas.professor import ProfessorCreate, ProfessorResponse, ProfessorUpdate

router = APIRouter()

@router.get("/", response_model=List[ProfessorResponse])
def read_professores(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Recupera a lista de professores."""
    professores = db.query(Professor).offset(skip).limit(limit).all()
    return professores

@router.post("/", response_model=ProfessorResponse, status_code=status.HTTP_201_CREATED)
def create_professor(professor: ProfessorCreate, db: Session = Depends(get_db)):
    """Cria um novo professor."""
    try:
        print(f"Tentando criar professor: {professor}")
        db_professor = Professor(**professor.dict())
        db.add(db_professor)
        db.commit()
        db.refresh(db_professor)
        print(f"Professor criado com sucesso: {db_professor}")
        return db_professor
    except Exception as e:
        db.rollback()
        # Imprimir detalhes do erro para facilitar depuração
        error_details = traceback.format_exc()
        print(f"Erro ao criar professor: {str(e)}")
        print(f"Detalhes do erro: {error_details}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao criar professor: {str(e)}"
        )

@router.get("/{professor_id}", response_model=ProfessorResponse)
def read_professor(professor_id: int, db: Session = Depends(get_db)):
    """Recupera informações de um professor específico."""
    professor = db.query(Professor).filter(Professor.id == professor_id).first()
    if professor is None:
        raise HTTPException(status_code=404, detail="Professor não encontrado")
    return professor

@router.put("/{professor_id}", response_model=ProfessorResponse)
def update_professor(professor_id: int, professor: ProfessorUpdate, db: Session = Depends(get_db)):
    """Atualiza um professor existente."""
    db_professor = db.query(Professor).filter(Professor.id == professor_id).first()
    if db_professor is None:
        raise HTTPException(status_code=404, detail="Professor não encontrado")
    
    for key, value in professor.dict(exclude_unset=True).items():
        setattr(db_professor, key, value)
    
    db.commit()
    db.refresh(db_professor)
    return db_professor

@router.delete("/{professor_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_professor(professor_id: int, db: Session = Depends(get_db)):
    """Remove um professor."""
    professor = db.query(Professor).filter(Professor.id == professor_id).first()
    if professor is None:
        raise HTTPException(status_code=404, detail="Professor não encontrado")
    
    db.delete(professor)
    db.commit()
    return None