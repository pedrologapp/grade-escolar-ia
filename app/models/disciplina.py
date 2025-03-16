from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from app.models.database import Base
from app.models.professor import professor_disciplina

class Disciplina(Base):
    __tablename__ = "disciplinas"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String, nullable=False)
    codigo = Column(String, unique=True, index=True, nullable=False)
    carga_horaria = Column(Integer, nullable=False)
    
    # Relacionamentos
    professores = relationship("Professor", secondary=professor_disciplina, back_populates="disciplinas")
    turmas = relationship("Turma", back_populates="disciplina")
    
    # Método para representação em string
    def __repr__(self):
        return f"Disciplina(id={self.id}, nome='{self.nome}', codigo='{self.codigo}')"