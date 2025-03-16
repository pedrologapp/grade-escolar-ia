import os
import json
from typing import Dict, Any, List
from sqlalchemy.orm import Session
from openai import OpenAI

from app.models.database import SessionLocal
from app.models.professor import Professor
from app.models.turma import Turma
from app.models.horario import Horario
from app.models.regra import Regra

class AIService:
    def __init__(self):
        """Inicializa o serviço de IA com a API da OpenAI."""
        self.api_key = os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            print("AVISO: OPENAI_API_KEY não configurada nas variáveis de ambiente")
            return
        
        self.client = OpenAI(api_key=self.api_key)
        self.model = "gpt-4-turbo"
        print("AI Service inicializado com OpenAI")

    def extrair_professores_do_texto(self, feedback: str) -> List[str]:
        """
        Usa a IA para identificar nomes de professores mencionados no feedback.
        Retorna uma lista com os nomes detectados.
        """
        prompt = f"""
        Extraia os nomes dos professores mencionados na seguinte mensagem e retorne apenas os nomes como uma lista em JSON:
        
        Mensagem: "{feedback}"

        Exemplo de resposta esperada:
        ["João", "Maria", "Carlos"]
        """

        response = self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "system", "content": prompt}],
            max_tokens=200
        )

        try:
            professores = json.loads(response.choices[0].message.content)
            return professores if isinstance(professores, list) else []
        except json.JSONDecodeError:
            return []

    def adicionar_professor(self, db: Session, nome: str, email: str, area: str) -> Dict[str, Any]:
        """
        Adiciona um novo professor ao banco de dados.
        """
        try:
            novo_professor = Professor(nome=nome, email=email, area=area)
            db.add(novo_professor)
            db.commit()
            db.refresh(novo_professor)
            return {"success": True, "message": f"Professor {nome} adicionado com sucesso!"}
        except Exception as e:
            db.rollback()
            return {"success": False, "error": f"Erro ao adicionar professor: {str(e)}"}

    def refine_schedule(self, current_schedule: Dict[str, Any], feedback: str, db: Session) -> Dict[str, Any]:
        """
        Refina a grade existente com base no feedback fornecido pelo usuário, preservando a estrutura original.
        Se um professor não existir, pergunta ao usuário se deseja cadastrá-lo.
        """
        try:
            if not feedback.strip():
                return {"success": False, "error": "Feedback vazio. Forneça informações detalhadas para o refinamento."}

            # Extraindo nomes dos professores mencionados no feedback
            professores_no_feedback = self.extrair_professores_do_texto(feedback)

            # Verificando se esses professores existem no banco de dados
            professores_existentes = {prof.nome for prof in db.query(Professor).all()}
            professores_para_cadastrar = []

            for professor in professores_no_feedback:
                if professor not in professores_existentes:
                    professores_para_cadastrar.append(professor)

            if professores_para_cadastrar:
                return {
                    "success": False,
                    "error": f"Os seguintes professores não estão cadastrados no sistema: {', '.join(professores_para_cadastrar)}. "
                             "Você deseja adicioná-los? Se sim, forneça nome, e-mail e área de atuação para cada professor."
                }

            # Se todos os professores existirem, prossegue com o refinamento da grade
            prompt = f"""
            Você é um assistente especializado em otimização de grade escolar.

            O usuário forneceu o seguinte feedback:
            "{feedback}"

            Aqui está a grade atual:
            {json.dumps(current_schedule, indent=2)}

            **Importante:**
            - NÃO remova nenhuma disciplina ou professor da grade existente.
            - Ajuste apenas os horários dos professores mencionados no feedback.
            - Se um professor estiver indisponível, realoque as aulas para outros professores disponíveis.
            - Mantenha a estrutura original da grade intacta.

            Retorne a nova grade em formato JSON, mantendo a estrutura original e aplicando apenas as alterações necessárias.
            """

            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "system", "content": prompt}],
                max_tokens=1000
            )

            try:
                new_schedule = json.loads(response.choices[0].message.content)
                return {"success": True, "schedule": new_schedule}
            except json.JSONDecodeError:
                return {"success": False, "error": "Erro ao processar a nova grade. A IA não retornou um JSON válido."}

        except Exception as e:
            return {"success": False, "error": f"Falha ao refinar a grade: {str(e)}"}

# Instância singleton do serviço
ai_service = AIService()