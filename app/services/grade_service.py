from typing import List, Dict, Any, Tuple
from sqlalchemy.orm import Session
from datetime import datetime, time
import traceback

from app.models.professor import Professor
from app.models.disciplina import Disciplina
from app.models.turma import Turma
from app.models.horario import Horario
from app.models.regra import Regra
from app.services.ai_service import ai_service
from app.services.rag_service import rag_service

class GradeService:
    def __init__(self):
        """Inicializa o serviço de grade escolar."""
        pass
    
    def _get_all_data(self, db: Session) -> Dict[str, List[Dict[str, Any]]]:
        """
        Recupera todos os dados necessários para a otimização da grade.
        
        Args:
            db: Sessão do banco de dados
            
        Returns:
            Dicionário com todos os dados
        """
        # Recuperar professores
        professors = db.query(Professor).all()
        professors_data = [
            {
                "id": p.id,
                "nome": p.nome,
                "email": p.email,
                "area": p.area
            }
            for p in professors
        ]
        
        # Recuperar disciplinas
        courses = db.query(Disciplina).all()
        courses_data = [
            {
                "id": c.id,
                "nome": c.nome,
                "codigo": c.codigo,
                "carga_horaria": c.carga_horaria
            }
            for c in courses
        ]
        
        # Recuperar turmas
        classes = db.query(Turma).all()
        classes_data = [
            {
                "id": t.id,
                "codigo": t.codigo,
                "periodo": t.periodo,
                "disciplina_id": t.disciplina_id
            }
            for t in classes
        ]
        
        # Recuperar regras
        rules = db.query(Regra).all()
        rules_data = [
            {
                "id": r.id,
                "nome": r.nome,
                "descricao": r.descricao,
                "tipo": r.tipo,
                "condicoes": r.condicoes
            }
            for r in rules
        ]
        
        return {
            "professors": professors_data,
            "courses": courses_data,
            "classes": classes_data,
            "rules": rules_data
        }
    
    def generate_initial_schedule(self, db: Session) -> Dict[str, Any]:
        """
        Gera uma grade inicial otimizada.
        
        Args:
            db: Sessão do banco de dados
            
        Returns:
            Grade otimizada
        """
        # Recuperar todos os dados
        data = self._get_all_data(db)
        
        # Gerar grade otimizada usando o serviço de IA
        result = ai_service.generate_schedule_optimization(
            professors=data["professors"],
            courses=data["courses"],
            classes=data["classes"],
            rules=data["rules"]
        )
        
        if result["success"]:
            # Aqui você poderia salvar a grade gerada no banco de dados
            # ou fazer qualquer processamento adicional
            return {
                "schedule": result["schedule"],
                "message": "Grade inicial gerada com sucesso!"
            }
        else:
            return {
                "error": result.get("error", "Erro desconhecido"),
                "message": "Falha ao gerar grade inicial."
            }
    
    def refine_schedule_with_feedback(self, current_schedule: Dict[str, Any], feedback: str) -> Dict[str, Any]:
        """
        Refina uma grade existente com base no feedback do usuário.
        
        Args:
            current_schedule: Grade atual
            feedback: Feedback do usuário
            
        Returns:
            Grade refinada
        """
        try:
            # Usar RAG para encontrar regras relevantes com base no feedback
            try:
                relevant_rules = rag_service.search_relevant_rules(feedback)
                
                # Enriquecer o feedback com regras relevantes, se houver
                enhanced_feedback = feedback
                if relevant_rules:
                    enhanced_feedback += "\n\nRegras relevantes para considerar:\n"
                    for rule in relevant_rules:
                        enhanced_feedback += f"\n{rule['content']}\n"
            except Exception as e:
                print(f"Erro ao usar RAG: {e}. Continuando sem enriquecimento de feedback.")
                enhanced_feedback = feedback
            
            # Refinar a grade com o feedback (enriquecido ou não)
            result = ai_service.refine_schedule(current_schedule, enhanced_feedback)
            
            if result["success"]:
                return {
                    "schedule": result["schedule"],
                    "message": "Grade refinada com sucesso!"
                }
            else:
                error_msg = result.get("error", "Erro desconhecido")
                print(f"Erro ao refinar grade: {error_msg}")
                return {
                    "error": error_msg,
                    "message": f"Falha ao refinar a grade: {error_msg}"
                }
        except Exception as e:
            print(f"Erro geral no método refine_schedule_with_feedback: {e}")
            import traceback
            traceback.print_exc()
            return {
                "error": str(e),
                "message": f"Falha ao refinar a grade: {str(e)}"
            }
    
    def save_schedule_to_database(self, db: Session, schedule_data: Dict[str, Any]) -> Tuple[bool, str]:
        """
        Salva a grade otimizada no banco de dados.
        
        Args:
            db: Sessão do banco de dados
            schedule_data: Dados da grade otimizada
            
        Returns:
            Tupla (sucesso, mensagem)
        """
        try:
            # Adicionar logs detalhados
            print(f"Recebendo dados para salvar: {schedule_data}")
            
            entries = schedule_data.get("entries", [])
            if not entries:
                return False, "Nenhuma entrada de horário para salvar"
            
            print(f"Número de entradas a salvar: {len(entries)}")
            
            # Verificar cada entrada para diagnóstico
            for i, entry in enumerate(entries):
                print(f"Entrada {i+1}: {entry}")
            
            # Converter a grade em objetos Horario e salvar
            horarios = []
            
            for entry in entries:
                try:
                    # Encontrar o ID do professor pelo nome
                    professor_name = entry.get("Professor")
                    professor = db.query(Professor).filter(Professor.nome == professor_name).first()
                    if not professor:
                        print(f"Professor não encontrado: {professor_name}")
                        return False, f"Professor não encontrado: {professor_name}"
                    
                    # Encontrar o ID da turma pelo código
                    turma_code = entry.get("Turma")
                    turma = db.query(Turma).filter(Turma.codigo == turma_code).first()
                    if not turma:
                        print(f"Turma não encontrada: {turma_code}")
                        return False, f"Turma não encontrada: {turma_code}"
                    
                    # Processar o formato de horário (ex: "08:00-09:00")
                    horario_str = entry.get("Horário", "")
                    print(f"Processando horário: {horario_str}")
                    
                    if "-" in horario_str:
                        hora_inicio_str, hora_fim_str = horario_str.split("-")
                        
                        # Converter para o formato adequado do banco de dados
                        hora_inicio = time(
                            int(hora_inicio_str.split(":")[0]), 
                            int(hora_inicio_str.split(":")[1])
                        )
                        hora_fim = time(
                            int(hora_fim_str.split(":")[0]), 
                            int(hora_fim_str.split(":")[1])
                        )
                        
                        print(f"Hora início: {hora_inicio}, Hora fim: {hora_fim}")
                    else:
                        print(f"Formato de horário inválido: {horario_str}")
                        return False, f"Formato de horário inválido: {horario_str}"
                    
                    # Criar objeto Horario
                    horario = Horario(
                        dia_semana=entry.get("Dia", ""),
                        hora_inicio=hora_inicio,
                        hora_fim=hora_fim,
                        sala=entry.get("Sala", ""),
                        professor_id=professor.id,
                        turma_id=turma.id
                    )
                    
                    print(f"Horário criado: {horario}")
                    horarios.append(horario)
                    
                except Exception as e:
                    print(f"Erro ao processar entrada {entry}: {e}")
                    error_details = traceback.format_exc()
                    print(f"Detalhes do erro: {error_details}")
                    return False, f"Erro ao processar entrada: {str(e)}"
            
            # Adicionar ao banco de dados
            if horarios:
                try:
                    print(f"Salvando {len(horarios)} horários")
                    
                    # Limpar horários existentes (opcional)
                    db.query(Horario).delete()
                    
                    # Adicionar novos horários
                    db.add_all(horarios)
                    db.commit()
                    print("Commit realizado com sucesso")
                    
                    return True, f"{len(horarios)} horários salvos com sucesso"
                except Exception as e:
                    db.rollback()
                    print(f"Erro ao salvar no banco: {e}")
                    error_details = traceback.format_exc()
                    print(f"Detalhes do erro: {error_details}")
                    return False, f"Erro ao salvar no banco: {str(e)}"
            else:
                return False, "Nenhum horário válido para salvar"
            
        except Exception as e:
            db.rollback()
            print(f"Erro geral ao salvar grade: {e}")
            error_details = traceback.format_exc()
            print(f"Detalhes do erro: {error_details}")
            return False, f"Erro geral ao salvar grade: {str(e)}"

# Instância singleton do serviço
grade_service = GradeService()