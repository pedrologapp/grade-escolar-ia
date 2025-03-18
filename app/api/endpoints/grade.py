import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../..")))
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, HTTPException, status, Body 
from typing import Dict, Any
from pydantic import BaseModel
import traceback

from ...models.database import get_db
from ...services.grade_service import grade_service

# Modelos Pydantic
class RefineRequest(BaseModel):
    feedback: str

router = APIRouter()

@router.post("/generate", response_model=Dict[str, Any])
def generate_schedule(db: Session = Depends(get_db)):
    """Gera uma grade escolar otimizada."""
    try:
        result = grade_service.generate_initial_schedule(db)
        if "error" in result:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=result["message"]
            )
        return result
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Erro ao gerar grade: {str(e)}")

@router.post("/refine", response_model=Dict[str, Any])
def refine_schedule(
    feedback: str = Body(...),
    db: Session = Depends(get_db)
):
    """Refina uma grade escolar existente com base no feedback."""
    try:
        print(f"Recebendo feedback para refinamento: {feedback}")
        result = grade_service.refine_schedule_with_feedback(feedback, db)
        if "error" in result:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=result["message"]
            )
        return result
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Falha ao refinar a grade: {str(e)}")

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
        from ...services.rag_service import rag_service
        rag_service.index_rules()
        return {"message": "Regras indexadas com sucesso!"}
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao indexar regras: {str(e)}"
        )
