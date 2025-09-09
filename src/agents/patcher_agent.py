# src/agents/patcher_agent.py

import subprocess
import os
from src.core.functional_agent import FunctionalAgent
from src.core.logger import get_logger

class PatcherAgent(FunctionalAgent):
    """
    Agente funcional que aplica patches a arquivos usando o comando 'patch'.
    """
    def __init__(self):
        super().__init__(agent_name="Patcher")
        self.logger = get_logger(self.agent_name)

    def run(self, file_path: str, patch_content: str):
        """
        Aplica um patch a um arquivo.

        Args:
            file_path: O caminho para o arquivo a ser modificado.
            patch_content: O conteúdo do patch no formato diff.
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Arquivo para aplicar patch não encontrado: {file_path}")

        patch_file_path = "workspace/temp.patch"
        try:
            # Escreve o conteúdo do patch em um arquivo temporário
            with open(patch_file_path, "w", encoding="utf-8") as f:
                f.write(patch_content)
            self.logger.info(f"Arquivo de patch temporário criado em {patch_file_path}")

            # Executa o comando 'patch' do sistema
            command = ["patch", file_path, patch_file_path]
            self.logger.info(f"Executando comando: {' '.join(command)}")
            result = subprocess.run(command, capture_output=True, text=True)

            if result.returncode != 0:
                self.logger.error(f"Falha ao aplicar o patch. Stderr:\n{result.stderr}")
                # Tenta reverter o patch se falhar
                revert_command = ["patch", "-R", file_path, patch_file_path]
                subprocess.run(revert_command)
                raise Exception(f"Falha ao aplicar o patch. Erro: {result.stderr}")
            
            self.logger.info(f"Patch aplicado com sucesso a {file_path}.")

        finally:
            # Garante que o arquivo de patch seja sempre removido
            if os.path.exists(patch_file_path):
                os.remove(patch_file_path)
                self.logger.info("Arquivo de patch temporário removido.")