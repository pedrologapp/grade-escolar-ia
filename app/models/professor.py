from sqlalchemy import Column, Integer, String, Table, ForeignKey
from sqlalchemy.orm import relationship
from app.models.database import Base

# Tabela de associação entre Professores e Disciplinas
professor_disciplina = Table(
    'professor_disciplina', 
    Base.metadata,
    Column('professor_id', Integer, ForeignKey('professores.id'), primary_key=True),
    Column('disciplina_id', Integer, ForeignKey('disciplinas.id'), primary_key=True)
)

class Professor(Base):
    __tablename__ = "professores"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    area = Column(String, nullable=True)
    
    # Relacionamentos
    disciplinas = relationship("Disciplina", secondary=professor_disciplina, back_populates="professores")
    horarios = relationship("Horario", back_populates="professor")