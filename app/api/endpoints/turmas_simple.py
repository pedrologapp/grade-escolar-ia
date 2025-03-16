from fastapi import APIRouter

router = APIRouter()

@router.get("/")
def read_turmas():
    """Teste de endpoint para turmas."""
    return {"message": "Endpoint de turmas funcionando!"}

@router.post("/")
def create_turma():
    """Teste de criação de turma."""
    return {"message": "Endpoint de criação de turma funcionando!"}