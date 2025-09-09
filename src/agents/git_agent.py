# src/agents/git_agent.py

import subprocess
# --- CORREÇÃO APLICADA AQUI ---
from src.core.functional_agent import FunctionalAgent

class GitAgent(FunctionalAgent):
    """
    Agente funcional responsável por interagir com o Git para
    commitar e enviar alterações para o repositório remoto.
    """
    def __init__(self):
        super().__init__(agent_name="GitAgent")

    def _run_command(self, command: list[str]):
        """Função auxiliar para executar um comando e tratar a saída."""
        try:
            print(f"[{self.agent_name}] Executando: '{' '.join(command)}'")
            subprocess.run(command, check=True, capture_output=True, text=True, encoding='utf-8')
            return True
        except subprocess.CalledProcessError as e:
            print(f"[{self.agent_name}] Erro ao executar comando: {' '.join(command)}")
            print(f"  - Erro: {e.stderr}")
            return False
        except FileNotFoundError:
            print(f"[{self.agent_name}] Erro: O comando 'git' não foi encontrado. O Git está instalado e no PATH do sistema?")
            return False

    def run(self, commit_message: str):
        """
        Executa a sequência de 'git add', 'git commit' e 'git push'.

        Args:
            commit_message: A mensagem a ser usada para o commit.
        """
        print(f"[{self.agent_name}] Iniciando processo de versionamento...")

        # 1. Git Add
        if not self._run_command(["git", "add", "."]):
            print(f"[{self.agent_name}] Falha no 'git add'. Abortando.")
            return

        # 2. Git Commit
        if not self._run_command(["git", "commit", "-m", commit_message]):
            print(f"[{self.agent_name}] Falha no 'git commit'. Pode não haver nada para commitar. Abortando.")
            return

        # 3. Git Push
        if not self._run_command(["git", "push", "origin", "main"]):
            print(f"[{self.agent_name}] Falha no 'git push'. Verifique a conexão e as credenciais.")
            return
            
        print(f"[{self.agent_name}] Alterações enviadas para o repositório com sucesso.")