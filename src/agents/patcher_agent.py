# src/agents/patcher_agent.py

import subprocess
import os
import shutil
from src.core.functional_agent import FunctionalAgent
from src.core.logger import get_logger

class PatcherAgent(FunctionalAgent):
    def __init__(self):
        super().__init__(agent_name="Patcher")
        self.logger = get_logger(self.agent_name)

    def run(self, file_path: str, patch_content: str):
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Arquivo para aplicar patch não encontrado: {file_path}")

        backup_path = f"{file_path}.bak"
        patch_file_path = "workspace/temp.patch"
        
        try:
            # 1. Criar backup
            shutil.copy2(file_path, backup_path)
            self.logger.info(f"Backup do arquivo original criado em {backup_path}")

            # 2. Escrever e aplicar patch
            with open(patch_file_path, "w", encoding="utf-8") as f:
                f.write(patch_content)
            
            command = ["patch", file_path, patch_file_path]
            self.logger.info(f"Executando comando: {' '.join(command)}")
            result = subprocess.run(command, capture_output=True, text=True)

            if result.returncode != 0:
                self.logger.error(f"Falha ao aplicar o patch. Stderr:\n{result.stderr}")
                # 3. Se falhar, restaurar o backup
                shutil.move(backup_path, file_path)
                self.logger.warning(f"Patch falhou. Arquivo original restaurado a partir de {backup_path}.")
                raise Exception(f"Falha ao aplicar o patch. Erro: {result.stderr}")
            
            self.logger.info(f"Patch aplicado com sucesso a {file_path}.")

        finally:
            # 4. Limpeza
            if os.path.exists(patch_file_path):
                os.remove(patch_file_path)
            if os.path.exists(backup_path):
                os.remove(backup_path) # Remove o backup se o patch foi bem-sucedido