import uvicorn
from fastapi import FastAPI
from dotenv import load_dotenv
from app.models.database import init_db
from contextlib import asynccontextmanager

# Tentar importar o router da API
try:
    from app.api.router import api_router
    has_api_router = True
except ImportError:
    print("AVISO: Router da API não encontrado ou com erro")
    has_api_router = False

# Carregar variáveis de ambiente
load_dotenv()

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Aplicação iniciando...")
    init_db()  # Inicializar o banco de dados na inicialização
    yield
    print("Aplicação encerrando...")

# Criar a aplicação FastAPI
app = FastAPI(
    title="Sistema de Otimização de Grade Escolar",
    description="API para otimização de grade escolar com IA",
    version="0.1.0",
    lifespan=lifespan
)

# Incluir o router da API se disponível
if has_api_router:
    app.include_router(api_router, prefix="/api")

# Rota básica para teste
@app.get("/")
async def root():
    return {"message": "Bem-vindo ao Sistema de Otimização de Grade Escolar"}

# Rota para verificação de saúde da API
@app.get("/health")
def health_check():
    return {"status": "ok", "message": "API funcionando corretamente"}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
