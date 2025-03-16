from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from app.models.database import Base

class Turma(Base):
    __tablename__ = "turmas"

    id = Column(Integer, primary_key=True, index=True)
    codigo = Column(String, unique=True, index=True, nullable=False)
    periodo = Column(String, nullable=False)
    
    # Chave estrangeira
    disciplina_id = Column(Integer, ForeignKey("disciplinas.id"), nullable=False)
    
    # Relacionamentos
    disciplina = relationship("Disciplina", back_populates="turmas")
    horarios = relationship("Horario", back_populates="turma")
    
    # Método para representação em string
    def __repr__(self):
        return f"Turma(id={self.id}, codigo='{self.codigo}', periodo='{self.periodo}')"