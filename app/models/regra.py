from sqlalchemy import Column, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from app.models.database import Base

class Regra(Base):
    __tablename__ = "regras"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String, nullable=False)
    descricao = Column(Text, nullable=True)
    tipo = Column(String, nullable=False)  # Ex: "Restrição", "Preferência"
    condicoes = Column(JSONB, nullable=False)  # Armazena condições em formato JSON
    
    # Método para representação em string
    def __repr__(self):
        return f"Regra(id={self.id}, nome='{self.nome}', tipo='{self.tipo}')"