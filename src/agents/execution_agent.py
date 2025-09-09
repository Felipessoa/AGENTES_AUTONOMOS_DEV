# src/agents/execution_agent.py

import subprocess
# --- CORREÇÃO APLICADA AQUI ---
from src.core.functional_agent import FunctionalAgent

class ExecutionAgent(FunctionalAgent):
    """
    Agente funcional responsável por executar comandos de linha de comando.
    """
    def __init__(self):
        super().__init__(agent_name="Executor")

    def run(self, command_to_execute: str):
        """
        Executa um comando de shell e imprime sua saída.

        Args:
            command_to_execute: A string completa do comando a ser executado.
        """
        print(f"[{self.agent_name}] Executando comando: '{command_to_execute}'")
        try:
            # Usando shlex.split para lidar com comandos complexos e evitar injeção de shell
            # No entanto, para simplicidade e compatibilidade com o orchestrator atual,
            # vamos manter shell=True, mas cientes do risco de segurança.
            # Em um sistema de produção, a entrada seria validada.
            result = subprocess.run(
                command_to_execute,
                shell=True,
                check=True,
                capture_output=True,
                text=True,
                encoding='utf-8'
            )
            print(f"[{self.agent_name}] Comando executado com sucesso.")
            if result.stdout:
                print("--- Saída (stdout) ---")
                print(result.stdout)
            if result.stderr:
                print("--- Erros (stderr) ---")
                print(result.stderr)
            
        except subprocess.CalledProcessError as e:
            print(f"[{self.agent_name}] Erro ao executar o comando.")
            print(f"  - Código de saída: {e.returncode}")
            if e.stdout:
                print("--- Saída (stdout) ---")
                print(e.stdout)
            if e.stderr:
                print("--- Erros (stderr) ---")
                print(e.stderr)
        except Exception as e:
            print(f"[{self.agent_name}] Ocorreu um erro inesperado: {e}")