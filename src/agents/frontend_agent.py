# src/agents/frontend_agent.py

import os
from src.core.base_agent import BaseAgent
from src.core.logger import get_logger

FRONTEND_DEV_SYSTEM_PROMPT = """
Você é um Desenvolvedor Frontend Sênior, um especialista em criar interfaces de usuário (UI) bonitas, funcionais e responsivas usando HTML, CSS e JavaScript moderno.
Sua tarefa é receber uma instrução e escrever o código completo para um único arquivo (geralmente .html).
O CSS e o JavaScript devem ser incluídos dentro do arquivo HTML usando as tags <style> e <script> para simplicidade, a menos que o plano especifique arquivos separados.
Sua resposta deve ser APENAS o bloco de código. Não inclua explicações ou texto extra.
"""

class FrontendAgent(BaseAgent):
    """
    Agente desenvolvedor cognitivo. Recebe tarefas do Arquiteto e escreve
    o código de frontend correspondente.
    """
    def __init__(self):
        super().__init__(
            agent_name="FrontendDev",
            system_prompt=FRONTEND_DEV_SYSTEM_PROMPT
        )
        self.logger = get_logger(self.agent_name)

    def write_code(self, file_path: str, task_description: str):
        """
        Gera o código de frontend para uma tarefa e o salva no arquivo.
        """
        self.logger.info(f"Iniciando a tarefa de design para o caminho final: '{file_path}'")
        self.logger.debug(f"Descrição da tarefa: {task_description}")

        generated_code = self.think(task_description)

        if generated_code and not generated_code.startswith("Erro:"):
            if "```" in generated_code:
                parts = generated_code.split('```')
                if len(parts) > 1:
                    code_block = parts[1]
                    first_line, *rest_of_lines = code_block.split('\n')
                    if first_line.lower().strip() in ['html', 'css', 'javascript', 'js']:
                        generated_code = '\n'.join(rest_of_lines)
                    else:
                        generated_code = '\n'.join([first_line] + rest_of_lines)
                    generated_code = generated_code.strip()

            try:
                parent_dir = os.path.dirname(file_path)
                os.makedirs(parent_dir, exist_ok=True)
                
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(generated_code)
                
                self.logger.info(f"Código de frontend para '{file_path}' escrito com sucesso.")
                return True
            except Exception as e:
                self.logger.error(f"Falha ao escrever o arquivo '{file_path}': {e}", exc_info=True)
                return False
        else:
            self.logger.error(f"O LLM falhou em gerar o código de frontend para a tarefa: {task_description}")
            return False

    def run(self, stop_event):
        """O FrontendAgent v3.0 é reativo."""
        self.logger.info("FrontendDev em modo de espera (reativo).")
        pass