# src/agents/frontend_agent.py

import os
import re
from .base_agent import BaseAgent

class FrontendAgent(BaseAgent):
    """
    Um agente de IA especializado em engenharia de frontend.
    """

    def __init__(self, workspace: str):
        """
        Inicializa o FrontendAgent.

        Args:
            workspace (str): O caminho para o diretório de trabalho do agente.
        """
        super().__init__(workspace)
        self.system_prompt = """
Você é um Engenheiro de Frontend Sênior altamente qualificado.
Sua especialidade é criar interfaces de usuário modernas, limpas e responsivas usando exclusivamente HTML, CSS e JavaScript puro.
Você não usa frameworks ou bibliotecas como React, Vue, Angular, jQuery ou Bootstrap.
Seu código deve ser bem estruturado, comentado e seguir as melhores práticas da web.
Você receberá um plano e sua tarefa é gerar o código completo para todos os arquivos de frontend (HTML, CSS, JavaScript) descritos no plano.
Sua resposta DEVE ser um único bloco de código JSON, contendo uma lista de comandos 'create_file'.
Não inclua nenhum texto, explicação ou markdown fora do bloco de código JSON.
O JSON deve ser estruturado da seguinte forma:
{
  "commands": [
    {
      "name": "create_file",
      "args": {
        "file_path": "caminho/completo/para/o/arquivo.html",
        "content": "<!DOCTYPE html>\\n<html>\\n..."
      }
    },
    {
      "name": "create_file",
      "args": {
        "file_path": "caminho/completo/para/o/arquivo.css",
        "content": "body {\\n  font-family: Arial, sans-serif;\\n..."
      }
    }
  ]
}
"""

    def run(self) -> str:
        """
        Executa a tarefa do agente: lê o plano e gera o código de frontend.

        Returns:
            str: Uma string JSON contendo os comandos para criar os arquivos de frontend.
        """
        plan_path = os.path.join(self.workspace, 'plan.md')

        try:
            with open(plan_path, 'r', encoding='utf-8') as f:
                plan_content = f.read()
        except FileNotFoundError:
            error_message = {
                "commands": [
                    {
                        "name": "error",
                        "args": {
                            "message": f"Erro: O arquivo 'plan.md' não foi encontrado no workspace '{self.workspace}'."
                        }
                    }
                ]
            }
            import json
            return json.dumps(error_message, indent=2)

        # Para simplificar e dar mais contexto ao LLM, vamos extrair as seções relevantes.
        # Por enquanto, passaremos o plano inteiro, pois o system_prompt já o orienta
        # a focar nos arquivos de frontend.
        
        prompt = f"""
Baseado no seguinte plano de desenvolvimento, gere o código completo para todos os arquivos de frontend (HTML, CSS, JavaScript).

PLANO:
```markdown
{plan_content}
```

Lembre-se, sua saída deve ser um único bloco de código JSON com uma lista de comandos `create_file` para cada arquivo de frontend.
"""

        response_json = self.think(prompt)
        return response_json
