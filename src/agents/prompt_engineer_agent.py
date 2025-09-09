# src/agents/prompt_engineer_agent.py

import json
from src.core.base_agent import BaseAgent
from src.core.logger import get_logger

PROMPT_ENGINEER_SYSTEM_PROMPT = """
Você é um Engenheiro de Prompts Sênior, um especialista em criar instruções para Modelos de Linguagem Generativos (LLMs) que sejam claras, inequívocas e que minimizem a chance de erro ou 'alucinação'.
Sua tarefa é receber uma solicitação de um usuário e um contexto (como código-fonte) e traduzir isso em um prompt perfeito para um LLM Arquiteto de Software.
Você deve adicionar restrições explícitas e regras para garantir que o LLM Arquiteto seja obediente e realize apenas a tarefa solicitada.
Sua saída deve ser APENAS o prompt otimizado ou o JSON de análise, sem nenhum outro texto, comentário ou explicação.
"""

class PromptEngineerAgent(BaseAgent):
    """
    Agente cognitivo que otimiza prompts de usuário e analisa a intenção
    para serem mais eficazes para outros agentes.
    """
    def __init__(self):
        super().__init__(
            agent_name="PromptEngineer",
            system_prompt=PROMPT_ENGINEER_SYSTEM_PROMPT
        )
        self.logger = get_logger(self.agent_name)

    def analyze_user_intent(self, user_input: str) -> dict:
        """
        Analisa a entrada do usuário para classificar a intenção e extrair parâmetros.
        """
        self.logger.debug(f"Analisando intenção do usuário: '{user_input}'")

        intent_analysis_prompt = f"""
        Analise a seguinte solicitação do usuário e a estruture em um objeto JSON.
        A solicitação é: "{user_input}"

        As intenções (intent) válidas são: "BUILD", "MODIFY", "DESIGN", "COMMIT", "RUN", "COMPILE", "UNKNOWN".
        Os parâmetros (params) dependem da intenção:
        - BUILD: precisa de "description".
        - MODIFY: precisa de "file_path" e "description". Usado APENAS para alterar o CONTEÚDO de um arquivo.
        - DESIGN: precisa de "description".
        - COMMIT: precisa de "commit_message".
        - RUN: precisa de "command_to_execute". Usado para comandos de terminal como ls, rm, pip, etc.
        - COMPILE: precisa de "script_path".

        Exemplos Detalhados:
        - "crie um app flask simples" -> {{"intent": "BUILD", "params": {{"description": "um app flask simples"}}}}
        - "altere o arquivo src/main.py para adicionar um log" -> {{"intent": "MODIFY", "params": {{"file_path": "src/main.py", "description": "adicionar um log"}}}}
        - "adicione um comentário no topo do orchestrator.py" -> {{"intent": "MODIFY", "params": {{"file_path": "src/core/orchestrator.py", "description": "adicionar um comentário no topo"}}}}
        - "salve meu trabalho com a mensagem 'correção de bug'" -> {{"intent": "COMMIT", "params": {{"commit_message": "correção de bug"}}}}
        - "execute o script de teste" -> {{"intent": "RUN", "params": {{"command_to_execute": "pytest"}}}}
        - "limpe a pasta workspace deletando arquivos temporários" -> {{"intent": "RUN", "params": {{"command_to_execute": "rm workspace/*.tmp"}}}}
        - "delete a pasta generated_project" -> {{"intent": "RUN", "params": {{"command_to_execute": "rm -r generated_project"}}}}

        Responda APENAS com o objeto JSON. Não adicione explicações.
        """
        
        response_text = self.think(intent_analysis_prompt)
        
        try:
            if "```" in response_text:
                response_text = response_text.split('```')[1].replace("json", "").strip()
            
            return json.loads(response_text)
        except (json.JSONDecodeError, IndexError) as e:
            self.logger.error(f"Falha ao decodificar a análise de intenção em JSON: {e}\nResposta recebida: {response_text}")
            return {"intent": "UNKNOWN", "params": {}}

    def optimize_creation_prompt(self, description: str) -> str:
        self.logger.debug(f"Otimizando prompt de criação para: '{description[:50]}...'")
        
        optimized_prompt = f"""
        Crie um plano de desenvolvimento detalhado para o seguinte pedido de criação.
        O plano deve incluir o nome do arquivo, a estrutura de pastas e o conteúdo completo de cada arquivo a ser criado.
        Seja literal e siga a descrição exatamente.

        **Pedido do usuário:** '{description}'
        """
        return optimized_prompt

    def optimize_modification_prompt(self, file_path: str, existing_code: str, description: str) -> str:
        """
        Otimiza um prompt para a MODIFICAÇÃO de um arquivo, solicitando o CÓDIGO COMPLETO.
        """
        self.logger.debug(f"Otimizando prompt de modificação para: {file_path}")
        
        optimized_prompt = f"""
        Sua tarefa é executar uma modificação cirúrgiica e literal no arquivo de código localizado em '{file_path}'.

        **REGRAS E RESTRIÇÕES ESTRITAS (LEIA COM ATENÇÃO E SIGA-AS):**
        1.  **NÃO ALTERE A LÓGICA EXISTENTE:** Você só deve aplicar a mudança solicitada. Não refatore, não renomeie variáveis, não adicione comentários e não altere o estilo do código que não esteja diretamente relacionado à tarefa.
        2.  **NÃO ADICIONE NOVAS DEPENDÊNCIAS:** Não adicione novas declarações de 'import' que não foram explicitamente solicitadas.
        3.  **SEJA LITERAL:** Aplique a mudança exatamente como descrita na solicitação.
        4.  **FORNEÇA O CÓDIGO COMPLETO:** Sua resposta final deve ser o código-fonte completo e atualizado do arquivo, com a pequena alteração aplicada. Não forneça apenas o trecho alterado, explicações ou comentários.

        **O CÓDIGO ATUAL COMPLETO DO ARQUIVO É:**
        ---
        {existing_code}
        ---

        **A MODIFICAÇÃO SOLICITADA É A SEGUINTE:**
        "{description}"

        Agora, forneça o novo código completo para o arquivo, sem nenhum texto adicional.
        """
        return optimized_prompt