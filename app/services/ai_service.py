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

# Remova a importação do rag_service daqui

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

    def extract_rules_from_feedback(self, feedback: str) -> Dict[str, Any]:
        """
        Extrai regras estruturadas a partir do feedback em linguagem natural.
        """
        try:
            prompt = f"""
            Analise o seguinte feedback do usuário sobre uma grade escolar e extraia regras estruturadas:
            
            "{feedback}"
            
            Extraia todas as regras, restrições e preferências mencionadas no formato JSON.
            Cada regra deve ter: professor, restrição, dias permitidos, horário máximo e ação necessária.
            
            Exemplo de formato:
            [
              {{
                "professor": "Carlos Silva",
                "restricao": "Não pode dar aulas",
                "dias_permitidos": ["Segunda", "Quarta", "Sexta"],
                "horario_maximo": "18:00",
                "acao": "Realocar aulas",
                "dados_extras": {{"motivo": "Compromisso pessoal"}}
              }}
            ]
            """
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "system", "content": prompt}],
                max_tokens=1000
            )
            
            return {"success": True, "rules": response.choices[0].message.content}
        except Exception as e:
            return {"success": False, "error": str(e)}

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
    
    def refine_schedule_with_feedback(self, feedback: str, db: Session) -> Dict[str, Any]:
        """
        Usa IA para interpretar o feedback e refinar a grade. 
        
        Caso alguma informação já exista na base de dados, continuar, caso contrário, pergunta ao usuário se deseja cadastrá-lo. Por exemplo: Lucas é um professor! Mas Lucas não 
        consta na base de dados, então pergunta se quer adiciona-lo!
        """
        print(f"Feedback recebido pela IA: {feedback}")
        
        # Verificar se existem professores mencionados que não estão cadastrados
        professores_no_feedback = self.extrair_professores_do_texto(feedback)
        
        if professores_no_feedback:
            # Verificando se esses professores existem no banco de dados
            professores_existentes = {prof.nome for prof in db.query(Professor).all()}
            professores_para_cadastrar = []
            
            for professor in professores_no_feedback:
                if professor not in professores_existentes:
                    professores_para_cadastrar.append(professor)
            
            # Se houver professores não cadastrados, perguntar ao usuário
            if professores_para_cadastrar:
                return {
                    "success": False,
                    "error": f"Os seguintes professores não estão cadastrados no sistema: {', '.join(professores_para_cadastrar)}. "
                            "Você deseja adicioná-los? Se sim, forneça nome, e-mail e área de atuação para cada professor."
                }
        
        # Aqui a IA interpreta o feedback e extrai regras
        regras_extraidas = self.extract_rules_from_feedback(feedback)
        
        if not regras_extraidas.get("success"):
            return {"error": "Erro ao extrair regras da IA.", "message": "Falha ao refinar a grade."}
        
        try:
            regras = json.loads(regras_extraidas.get("rules", "[]"))
        except json.JSONDecodeError:
            return {"error": "Erro ao decodificar regras extraídas", "message": "Falha ao interpretar as regras."}
        
        # Salvar as regras no banco usando uma nova função interna
        for regra in regras:
            self._salvar_regra_no_banco(
                db,
                professor=regra.get("professor", "Desconhecido"),
                restricao=regra.get("restricao", "Não especificada"),
                dias_permitidos=regra.get("dias_permitidos", []),
                horario_maximo=regra.get("horario_maximo", "Não especificado"),
                acao=regra.get("acao", "Nenhuma ação"),
                dados_extras=regra.get("dados_extras", {})
            )
        
        print("Regras extraídas e salvas com sucesso!")
        
        return {
            "success": True,
            "schedule": "Grade refinada com as novas regras!",
            "message": "Grade refinada com sucesso!"
        }
        
    def _salvar_regra_no_banco(self, db: Session, professor: str, restricao: str, 
                               dias_permitidos: list, horario_maximo: str, acao: str, 
                               dados_extras: dict = None):
        """
        Salva uma regra no banco de dados.
        """
        try:
            nova_regra = Regra(
                nome=f"Regra para {professor}",
                descricao=restricao,
                tipo="Restrição",
                condicoes={
                    "professor": professor,
                    "restricao": restricao,
                    "dias_permitidos": dias_permitidos,
                    "horario_maximo": horario_maximo,
                    "acao": acao,
                    "dados_extras": dados_extras
                }
            )
            db.add(nova_regra)
            db.commit()
            db.refresh(nova_regra)
            return nova_regra
        except Exception as e:
            db.rollback()
            print(f"Erro ao salvar regra: {str(e)}")
            return None

# Instância singleton do serviço
ai_service = AIService()