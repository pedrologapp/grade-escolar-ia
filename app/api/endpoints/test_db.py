from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import text

from app.models.database import get_db

router = APIRouter()

@router.get("/connection")
def test_database_connection(db: Session = Depends(get_db)):
    """Testa a conexão com o banco de dados."""
    try:
        # Executar uma consulta SQL simples
        result = db.execute(text("SELECT 1")).fetchone()
        
        # Listar as tabelas existentes no banco de dados
        tables = db.execute(text("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'")).fetchall()
        table_names = [table[0] for table in tables]
        
        return {
            "status": "success", 
            "message": "Conexão com o PostgreSQL estabelecida com sucesso!",
            "query_result": result[0],
            "existing_tables": table_names
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro de conexão com o banco de dados: {str(e)}")