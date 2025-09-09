# src/agents/git_agent.py

import subprocess
from src.core.functional_agent import FunctionalAgent
from src.core.logger import get_logger

# Agente responsável pelas operações Git.

class GitAgent(FunctionalAgent):
    def __init__(self):
        super().__init__(agent_name="GitAgent")
        self.logger = get_logger(self.agent_name)

    def _run_command(self, command: list[str]):
        try:
            self.logger.info(f"Executando: '{' '.join(command)}'")
            result = subprocess.run(command, check=True, capture_output=True, text=True, encoding='utf-8')
            self.logger.debug(f"Saída de '{' '.join(command)}': {result.stdout}")
            return True
        except subprocess.CalledProcessError as e:
            self.logger.error(f"Erro ao executar comando: {' '.join(command)}\n{e.stderr}")
            print(f"[USER] ❌ Erro no Git: {e.stderr}")
            return False
        except FileNotFoundError:
            self.logger.critical("O comando 'git' não foi encontrado. O Git está instalado e no PATH?")
            print("[USER] ❌ Erro Crítico: O comando 'git' não foi encontrado.")
            return False

    def run(self, commit_message: str):
        print(f"[USER] Iniciando processo de versionamento...")
        self.logger.info(f"Iniciando processo de versionamento com a mensagem: '{commit_message}'")

        if not self._run_command(["git", "add", "."]):
            print(f"[USER] ❌ Falha no 'git add'. Abortando.")
            return

        if not self._run_command(["git", "commit", "-m", commit_message]):
            print(f"[USER] ⚠️ Falha no 'git commit'. Pode não haver nada para commitar. Verifique os logs.")
            return

        if not self._run_command(["git", "push", "origin", "main"]):
            print(f"[USER] ❌ Falha no 'git push'. Verifique a conexão e as credenciais.")
            return
            
        print(f"[USER] ✅ Alterações enviadas para o repositório com sucesso.")