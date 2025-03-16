from fastapi import APIRouter

api_router = APIRouter()

# Importar e incluir router de professores
try:
    from app.api.endpoints import professores
    api_router.include_router(professores.router, prefix="/professores", tags=["professores"])
except Exception as e:
    print(f"Erro ao importar router de professores: {e}")

# Importar e incluir router de disciplinas
try:
    from app.api.endpoints import disciplinas
    api_router.include_router(disciplinas.router, prefix="/disciplinas", tags=["disciplinas"])
except Exception as e:
    print(f"Erro ao importar router de disciplinas: {e}")

# Importar e incluir router de turmas
try:
    from app.api.endpoints import turmas
    api_router.include_router(turmas.router, prefix="/turmas", tags=["turmas"])
except Exception as e:
    print(f"Erro ao importar router de turmas: {e}")

# Importar e incluir router de horários
try:
    from app.api.endpoints import horarios
    api_router.include_router(horarios.router, prefix="/horarios", tags=["horarios"])
except Exception as e:
    print(f"Erro ao importar router de horários: {e}")

# Importar e incluir router de regras
try:
    from app.api.endpoints import regras
    api_router.include_router(regras.router, prefix="/regras", tags=["regras"])
except Exception as e:
    print(f"Erro ao importar router de regras: {e}")

# Importar e incluir router de grade
try:
    from app.api.endpoints import grade
    api_router.include_router(grade.router, prefix="/grade", tags=["Grade"])
except Exception as e:
    print(f"Erro ao importar router de grade: {e}")
