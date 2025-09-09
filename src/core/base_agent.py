# src/core/base_agent.py

import os
import google.generativeai as genai
from google.generativeai.types import GenerationConfig

class BaseAgent:
    """
    Classe base para todos os agentes cognitivos (baseados em LLM).
    """
    def __init__(self, agent_name: str, system_prompt: str, model_name="gemini-1.5-pro-latest"):
        self.agent_name = agent_name
        self.system_prompt = system_prompt
        
        self._configure_api_key()
        
        self.generation_config = GenerationConfig(temperature=0.7)
        
        self.model = genai.GenerativeModel(
            model_name=model_name,
            generation_config=self.generation_config,
            system_instruction=self.system_prompt
        )
        
        self.chat = self.model.start_chat(history=[])

    def _configure_api_key(self):
        api_key = os.environ.get("GEMINI_API_KEY")
        if not api_key:
            raise ValueError(f"[{self.agent_name}] A variável de ambiente GEMINI_API_KEY não foi encontrada.")
        genai.configure(api_key=api_key)

    def think(self, user_prompt: str) -> str:
        """

        Envia um prompt para o modelo e retorna a resposta completa.
        """
        try:
            response = self.chat.send_message(user_prompt)
            return response.text
        except Exception as e:
            return f"Erro: Não consegui processar o pedido. Detalhes: {e}"

    def write_to_workspace(self, filename: str, content: str):
        """Escreve/sobrescreve um arquivo no workspace."""
        filepath = os.path.join('workspace', filename)
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
        except Exception as e:
            print(f"[{self.agent_name}] Erro ao escrever em '{filepath}': {e}")

    def read_from_workspace(self, filename: str) -> str | None:
        """Lê um arquivo do workspace."""
        filepath = os.path.join('workspace', filename)
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                return f.read()
        except FileNotFoundError:
            return None
        except Exception as e:
            print(f"[{self.agent_name}] Erro ao ler '{filepath}': {e}")
            return None