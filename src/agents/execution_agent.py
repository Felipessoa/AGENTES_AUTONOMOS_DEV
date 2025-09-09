# src/agents/execution_agent.py

import subprocess
# --- CORREÇÃO DE IMPORTAÇÃO APLICADA AQUI ---
from src.core.functional_agent import FunctionalAgent
from src.core.logger import get_logger
# Importando o SecurityAgent para consulta
from src.agents.security_agent import SecurityAgent

class ExecutionAgent(FunctionalAgent):
    """
    Agente funcional responsável por executar comandos de linha de comando,
    após verificação de segurança.
    """
    def __init__(self):
        super().__init__(agent_name="Executor")
        self.logger = get_logger(self.agent_name)
        # Cria uma instância do SecurityAgent para usar como validador
        self.security_agent = SecurityAgent()

    def run(self, command_to_execute: str):
        """
        Analisa um comando e, se for seguro, o executa e imprime sua saída.

        Args:
            command_to_execute: A string completa do comando a ser executado.
        """
        self.logger.info(f"Recebido pedido para executar comando: '{command_to_execute}'")

        # --- Etapa de Verificação de Segurança ---
        security_check = self.security_agent.analyze_command(command_to_execute)
        
        if not security_check.get("approved"):
            reason = security_check.get("reason", "Motivo não especificado.")
            print(f"[USER] ❌ Execução bloqueada pelo Agente de Segurança.")
            print(f"[USER] Motivo: {reason}")
            self.logger.warning(f"Execução do comando '{command_to_execute}' bloqueada. Motivo: {reason}")
            return

        # --- Etapa de Execução ---
        self.logger.info(f"Comando aprovado. Executando: '{command_to_execute}'")
        print(f"[USER] Comando aprovado. Executando...")
        try:
            result = subprocess.run(
                command_to_execute,
                shell=True,
                check=True,
                capture_output=True,
                text=True,
                encoding='utf-8'
            )
            
            print(f"[USER] ✅ Comando executado com sucesso.")
            if result.stdout:
                print("--- Saída (stdout) ---")
                print(result.stdout.strip())
            if result.stderr:
                print("--- Erros (stderr) ---")
                print(result.stderr.strip())
            
        except subprocess.CalledProcessError as e:
            print(f"[USER] ❌ Erro ao executar o comando (código de saída: {e.returncode}).")
            if e.stdout:
                print("--- Saída (stdout) ---")
                print(e.stdout.strip())
            if e.stderr:
                print("--- Erros (stderr) ---")
                print(e.stderr.strip())
            self.logger.error(f"Erro de subprocesso ao executar '{command_to_execute}': {e.stderr}")
        except Exception as e:
            print(f"[USER] ❌ Ocorreu um erro inesperado durante a execução.")
            self.logger.error(f"Erro inesperado ao executar '{command_to_execute}': {e}", exc_info=True)