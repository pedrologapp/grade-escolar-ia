from sqlalchemy import Column, Integer, String, ForeignKey, Time
from sqlalchemy.orm import relationship
from app.models.database import Base

class Horario(Base):
    __tablename__ = "horarios"

    id = Column(Integer, primary_key=True, index=True)
    dia_semana = Column(String, nullable=False)  # Ex: "Segunda", "Terça", etc.
    hora_inicio = Column(Time, nullable=False)
    hora_fim = Column(Time, nullable=False)
    sala = Column(String, nullable=True)
    
    # Chaves estrangeiras
    professor_id = Column(Integer, ForeignKey("professores.id"), nullable=False)
    turma_id = Column(Integer, ForeignKey("turmas.id"), nullable=False)
    
    # Relacionamentos
    professor = relationship("Professor", back_populates="horarios")
    turma = relationship("Turma", back_populates="horarios")
    
    # Método para representação em string
    def __repr__(self):
        return f"Horario(id={self.id}, dia='{self.dia_semana}', inicio='{self.hora_inicio}', fim='{self.hora_fim}')"