# src/core/base_agent.py

import os
import google.generativeai as genai
from google.generativeai.types import GenerationConfig

class BaseAgent:
    """
    Classe base para todos os agentes do sistema.
    Fornece funcionalidades comuns como configuração da API,
    interação com o modelo LLM e acesso ao workspace.
    """
    def __init__(self, agent_name: str, system_prompt: str, model_name="gemini-2.5-pro"):
        self.agent_name = agent_name
        self.system_prompt = system_prompt
        
        # Configura a API key. Lança um erro se não for encontrada.
        self._configure_api_key()
        
        # Configurações de geração do modelo
        self.generation_config = GenerationConfig(temperature=0.7)
        
        # Inicializa o modelo generativo com a instrução de sistema
        self.model = genai.GenerativeModel(
            model_name=model_name,
            generation_config=self.generation_config,
            system_instruction=self.system_prompt
        )
        
        # Inicia a sessão de chat. O histórico será gerenciado aqui.
        self.chat = self.model.start_chat(history=[])
        print(f"Agente '{self.agent_name}' inicializado com o modelo '{model_name}'.")

    def _configure_api_key(self):
        """Método privado para configurar a chave da API."""
        api_key = os.environ.get("GEMINI_API_KEY")
        if not api_key:
            raise ValueError(f"[{self.agent_name}] A variável de ambiente GEMINI_API_KEY não foi encontrada.")
        genai.configure(api_key=api_key)

    def think(self, user_prompt: str) -> str:
        """
        Envia um prompt para o modelo e retorna a resposta completa.
        Este é um método de "pensamento" de um turno.
        """
        try:
            print(f"[{self.agent_name}] Pensando sobre: '{user_prompt[:50]}...'")
            response = self.chat.send_message(user_prompt)
            return response.text
        except Exception as e:
            print(f"[{self.agent_name}] Erro ao pensar: {e}")
            return f"Erro: Não consegui processar o pedido. Detalhes: {e}"

    def run(self, **kwargs):
        """
        O ponto de entrada principal para a lógica do agente.
        Este método deve ser sobrescrito por cada agente filho.
        """
        raise NotImplementedError("O método 'run' deve ser implementado pela subclasse.")

    # --- Métodos de Interação com o Workspace ---

    def write_to_workspace(self, filename: str, content: str):
        """Escreve/sobrescreve um arquivo no workspace."""
        filepath = os.path.join('workspace', filename)
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"[{self.agent_name}] Escreveu em '{filepath}'")
        except Exception as e:
            print(f"[{self.agent_name}] Erro ao escrever em '{filepath}': {e}")

    def read_from_workspace(self, filename: str) -> str | None:
        """Lê um arquivo do workspace."""
        filepath = os.path.join('workspace', filename)
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                return f.read()
        except FileNotFoundError:
            print(f"[{self.agent_name}] Arquivo não encontrado em '{filepath}'")
            return None
        except Exception as e:
            print(f"[{self.agent_name}] Erro ao ler '{filepath}': {e}")
            return None