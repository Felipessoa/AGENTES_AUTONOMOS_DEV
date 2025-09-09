# src/agents/git_agent.py

import subprocess
from src.core.functional_agent import FunctionalAgent

class GitAgent(FunctionalAgent):
    """
    Um agente funcional para interagir com o Git.
    Este agente pode adicionar, commitar e enviar alterações para um repositório.
    """

    def __init__(self):
        """
        Inicializa o GitAgent.
        """
        super().__init__(agent_name="GitAgent")

    def run(self, commit_message: str):
        """
        Executa a sequência de comandos Git: add, commit e push.

        Args:
            commit_message (str): A mensagem a ser usada para o commit.

        Returns:
            bool: True se todos os comandos foram executados com sucesso, False caso contrário.
        """
        if not commit_message:
            print("Erro: A mensagem de commit não pode ser vazia.")
            return False

        commands = [
            ("Adicionando todos os arquivos", ["git", "add", "."]),
            (f"Commitando com a mensagem: '{commit_message}'", ["git", "commit", "-m", commit_message]),
            ("Enviando para o repositório remoto", ["git", "push"])
        ]

        print(f"[{self.agent_name}] Iniciando sequência de comandos Git...")

        for description, command in commands:
            try:
                print(f"[{self.agent_name}] {description}...")
                # Usamos subprocess.run para executar o comando.
                # check=True garante que uma exceção CalledProcessError seja levantada se o comando falhar.
                # capture_output=True captura stdout e stderr.
                # text=True decodifica stdout e stderr como strings.
                result = subprocess.run(
                    command,
                    check=True,
                    capture_output=True,
                    text=True
                )
                # Imprime a saída padrão do comando se houver alguma
                if result.stdout:
                    print(result.stdout)
                print(f"[{self.agent_name}] Comando executado com sucesso.")

            except FileNotFoundError:
                print(f"[{self.agent_name}] Erro: O comando 'git' não foi encontrado. O Git está instalado e no PATH do sistema?")
                return False
            except subprocess.CalledProcessError as e:
                # Se o comando retornar um código de saída diferente de zero, um erro será capturado.
                print(f"[{self.agent_name}] Erro ao executar o comando: {' '.join(command)}")
                print(f"[{self.agent_name}] Código de Saída: {e.returncode}")
                print(f"[{self.agent_name}] Saída Padrão (stdout):\n{e.stdout}")
                print(f"[{self.agent_name}] Saída de Erro (stderr):\n{e.stderr}")
                return False
            except Exception as e:
                print(f"[{self.agent_name}] Ocorreu um erro inesperado: {e}")
                return False

        print(f"[{self.agent_name}] Sequência de comandos Git concluída com sucesso.")
        return True
