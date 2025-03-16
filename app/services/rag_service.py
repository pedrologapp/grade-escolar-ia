import os
from sqlalchemy.orm import Session
from typing import List, Dict, Any
from langchain_openai import OpenAIEmbeddings
from langchain.schema import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter
from sqlalchemy import create_engine
from langchain_community.vectorstores import PGVector
import json

from app.models.database import SessionLocal
from app.models.regra import Regra
from app.services.ai_service import ai_service

class RAGService:
    def __init__(self):
        """Inicializa o serviço RAG com embeddings da OpenAI e PGVector."""
        self.initialized = False
        try:
            openai_api_key = os.getenv("OPENAI_API_KEY")
            if not openai_api_key:
                print("AVISO: OPENAI_API_KEY não configurada nas variáveis de ambiente")
                return
                
            self.embeddings = OpenAIEmbeddings(openai_api_key=openai_api_key)
            self.connection_string = os.getenv("DATABASE_URI", "postgresql://postgres:postgres@localhost:5432/grade_escolar")
            
            self.collection_name = "grade_rules"
            self.vectorstore = None
            print("RAG Service inicializado sem PGVector")
            self.initialized = True
        except Exception as e:
            print(f"Erro ao inicializar RAG Service: {e}")
    
    def initialize_vectorstore(self):
        """Inicializa o vectorstore sob demanda."""
        if not self.initialized:
            print("RAG Service não foi inicializado corretamente")
            return False
            
        try:
            from langchain.vectorstores.pgvector import PGVector
            
            self.vectorstore = PGVector(
                collection_name=self.collection_name,
                connection_string=self.connection_string,
                embedding_function=self.embeddings
            )
            return True
        except Exception as e:
            print(f"Erro ao inicializar vectorstore: {e}")
            return False
    
    def index_rules(self):
        """Indexa todas as regras no banco de dados para pesquisa vetorial."""
        if not self.initialize_vectorstore():
            return {"success": False, "message": "Não foi possível inicializar o vectorstore"}
            
        db = SessionLocal()
        try:
            rules = db.query(Regra).all()
            
            if not rules:
                print("Nenhuma regra encontrada para indexação.")
                return {"success": False, "message": "Nenhuma regra encontrada"}
            
            documents = []
            for rule in rules:
                text = f"Regra {rule.id}: {rule.nome}\nTipo: {rule.tipo}\nDescrição: {rule.descricao}\nCondições: {rule.condicoes}"
                
                doc = Document(
                    page_content=text,
                    metadata={
                        "id": rule.id,
                        "nome": rule.nome,
                        "tipo": rule.tipo
                    }
                )
                documents.append(doc)
            
            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=1000,
                chunk_overlap=200
            )
            splits = text_splitter.split_documents(documents)
            
            self.vectorstore.add_documents(splits)
            
            print(f"Indexadas {len(splits)} partes de {len(documents)} regras com sucesso.")
            return {"success": True, "message": f"Indexadas {len(splits)} partes de {len(documents)} regras"}
            
        except Exception as e:
            print(f"Erro ao indexar regras: {e}")
            return {"success": False, "message": f"Erro: {str(e)}"}
        finally:
            db.close()
    
    def search_relevant_rules(self, query: str, k: int = 5) -> List[Dict[str, Any]]:
        """
        Busca regras relevantes com base em uma consulta.
        """
        # Se o vectorstore não estiver disponível, retorne uma lista vazia
        # mas não bloqueie o fluxo principal
        if not self.vectorstore:
            try:
                if not self.initialize_vectorstore():
                    print("Não foi possível inicializar o vectorstore. Continuando sem RAG.")
                    return []
            except Exception as e:
                print(f"Erro ao inicializar vectorstore: {e}")
                return []
                
        try:
            results = self.vectorstore.similarity_search_with_score(query, k=k)
            
            relevant_rules = []
            for doc, score in results:
                relevant_rules.append({
                    "content": doc.page_content,
                    "metadata": doc.metadata,
                    "score": score
                })
            
            return relevant_rules
        except Exception as e:
            print(f"Erro ao buscar regras: {e}")
            return []
          

def salvar_regra(db: Session, professor: str, restricao: str, dias_permitidos: list, horario_maximo: str, acao: str, dados_extras: dict = None):
    """
    Salva uma nova regra extraída pela IA no banco de dados, permitindo armazenar novos tipos de regras dinamicamente.
    """
    try:
        if db is None:
            db = SessionLocal()
        
        nova_regra = Regra(
            professor=professor,
            restricao=restricao,
            dias_permitidos=','.join(dias_permitidos),
            horario_maximo=horario_maximo,
            acao=acao,
            dados_extras=json.dumps(dados_extras) if dados_extras else None
        )
        db.add(nova_regra)
        db.commit()
        db.refresh(nova_regra)
        return nova_regra
    except Exception as e:
        db.rollback()
        print(f"Erro ao salvar regra: {str(e)}")
        return None

def extrair_e_salvar_regras(db: Session, feedback: str):
    """
    Usa a IA para extrair regras a partir do feedback e salva no banco de dados.
    """
    regras_extraidas = ai_service.extract_rules_from_feedback(feedback)
    
    if not regras_extraidas.get("success"):
        print("Erro ao extrair regras da IA.")
        return None
    
    try:
        regras = json.loads(regras_extraidas.get("rules", "[]"))
    except json.JSONDecodeError:
        print("Erro ao decodificar as regras extraídas da IA.")
        return None
    
    for regra in regras:
        salvar_regra(
            db,
            professor=regra.get("professor", "Desconhecido"),
            restricao=regra.get("restricao", "Não especificada"),
            dias_permitidos=regra.get("dias_permitidos", []),
            horario_maximo=regra.get("horario_maximo", "Não especificado"),
            acao=regra.get("acao", "Nenhuma ação"),
            dados_extras=regra.get("dados_extras", {})
        )
    
    print("Regras extraídas e salvas com sucesso!")

# Instância singleton do serviço
rag_service = RAGService()