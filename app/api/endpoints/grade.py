from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, HTTPException, status, Body
from typing import Dict, Any
from pydantic import BaseModel

from app.models.database import get_db
from app.services.grade_service import grade_service

# Define um modelo Pydantic para a requisição de refinamento
class RefineRequest(BaseModel):
    current_schedule: Dict[str, Any]
    feedback: str

router = APIRouter()

@router.post("/generate", response_model=Dict[str, Any])
def generate_schedule(db: Session = Depends(get_db)):
    """Gera uma grade escolar otimizada."""
    result = grade_service.generate_initial_schedule(db)
    
    if "error" in result:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=result["message"]
        )
    
    return result

@router.post("/refine", response_model=Dict[str, Any])
def refine_schedule(
    request: RefineRequest,
    db: Session = Depends(get_db)
):
    """Refina uma grade escolar existente com base no feedback."""
    result = grade_service.refine_schedule_with_feedback(
        request.current_schedule, 
        request.feedback
    )
    
    if "error" in result:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=result["message"]
        )
    
    return result

@router.post("/save", response_model=Dict[str, Any])
def save_schedule(
    schedule_data: Dict[str, Any],
    db: Session = Depends(get_db)
):
    """Salva uma grade otimizada no banco de dados."""
    try:
        print(f"Tentando salvar grade com dados: {schedule_data}")
        success, message = grade_service.save_schedule_to_database(db, schedule_data)
        
        if not success:
            print(f"Falha ao salvar grade: {message}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Falha ao salvar a grade no banco de dados: {message}"
            )
        
        return {"message": message}
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        print(f"Erro ao salvar grade: {str(e)}")
        print(f"Detalhes do erro: {error_details}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Falha ao salvar a grade no banco de dados: {str(e)}"
        )

@router.post("/index-rules", response_model=Dict[str, Any])
def index_rules():
    """Indexa todas as regras para RAG."""
    try:
        from app.services.rag_service import rag_service
        rag_service.index_rules()
        return {"message": "Regras indexadas com sucesso!"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao indexar regras: {str(e)}"
        )