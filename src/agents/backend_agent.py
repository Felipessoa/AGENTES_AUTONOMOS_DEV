# src/agents/backend_agent.py

import os
from src.core.base_agent import BaseAgent
from src.core.logger import get_logger

BACKEND_DEV_SYSTEM_PROMPT = """
Você é um Desenvolvedor de Software Sênior especialista em Python.
Sua tarefa é receber uma instrução de uma tarefa específica, que faz parte de um plano de desenvolvimento maior, e escrever o código Python completo e funcional para essa tarefa.
Você deve escrever código limpo, eficiente e bem documentado.
Siga a instrução da tarefa à risca. Se a tarefa pedir para criar a lógica para mover um círculo, escreva apenas o código para isso.
Sua resposta deve ser APENAS o bloco de código Python. Não inclua explicações, comentários fora do código ou qualquer outro texto.
"""

class BackendAgent(BaseAgent):
    """
    Agente desenvolvedor cognitivo. Recebe tarefas do Arquiteto e escreve
    o código Python correspondente.
    """
    def __init__(self):
        super().__init__(
            agent_name="BackendDev",
            system_prompt=BACKEND_DEV_SYSTEM_PROMPT
        )
        self.logger = get_logger(self.agent_name)

    def write_code(self, file_path: str, task_description: str):
        """
        Gera o código para uma tarefa específica e o salva no arquivo correspondente.
        """
        self.logger.info(f"Iniciando a tarefa de codificação para o caminho final: '{file_path}'")
        self.logger.debug(f"Descrição da tarefa: {task_description}")

        generated_code = self.think(task_description)

        if generated_code and not generated_code.startswith("Erro:"):
            if "```" in generated_code:
                parts = generated_code.split('```')
                if len(parts) > 1:
                    code_block = parts[1]
                    if code_block.lower().startswith(('python', 'py')):
                        generated_code = '\n'.join(code_block.split('\n')[1:])
                    else:
                        generated_code = code_block
                    generated_code = generated_code.strip()

            try:
                parent_dir = os.path.dirname(file_path)
                os.makedirs(parent_dir, exist_ok=True)
                
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(generated_code)
                
                self.logger.info(f"Código para '{file_path}' escrito com sucesso.")
                return True
            except Exception as e:
                self.logger.error(f"Falha ao escrever o arquivo '{file_path}': {e}", exc_info=True)
                return False
        else:
            self.logger.error(f"O LLM falhou em gerar o código para a tarefa: {task_description}")
            return False

    def run(self, stop_event):
        """O BackendAgent v3.0 é reativo."""
        self.logger.info("BackendDev em modo de espera (reativo).")
        pass