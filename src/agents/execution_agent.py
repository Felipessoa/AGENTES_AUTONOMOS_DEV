# src/agents/execution_agent.py

import subprocess
from src.core.functional_agent import FunctionalAgent
from src.core.logger import get_logger
from src.agents.security_agent import SecurityAgent

class ExecutionAgent(FunctionalAgent):
    """
    Agente funcional responsável por executar comandos de linha de comando,
    com verificação de existência e consulta de segurança.
    """
    def __init__(self):
        super().__init__(agent_name="Executor")
        self.logger = get_logger(self.agent_name)
        self.security_agent = SecurityAgent()

    def _command_exists(self, cmd: str) -> bool:
        """Verifica se um comando existe no PATH do sistema."""
        # Usa 'shutil.which' que é a forma mais robusta e multiplataforma em Python 3.3+
        from shutil import which
        return which(cmd) is not None

    def run(self, command_to_execute: str, skip_security_check=False) -> dict:
        """
        Executa um comando de shell após as verificações.

        Args:
            command_to_execute: A string completa do comando.
            skip_security_check: Se True, pula a análise de segurança (usado após confirmação do usuário).

        Returns:
            Um dicionário com o status da execução.
        """
        self.logger.info(f"Recebido pedido para executar comando: '{command_to_execute}'")
        
        # 1. Verifica se o comando existe
        main_command = command_to_execute.split()[0]
        if not self._command_exists(main_command):
            message = f"O comando '{main_command}' não foi encontrado no sistema. Verifique se a dependência está instalada."
            print(f"[USER] ❌ Erro: {message}")
            self.logger.error(message)
            return {"success": False, "reason": message}

        # 2. Análise de Segurança (a menos que seja pulada)
        if not skip_security_check:
            security_check = self.security_agent.analyze_command(command_to_execute)
            if security_check["status"] == "needs_confirmation":
                self.logger.warning(f"Comando '{command_to_execute}' precisa de confirmação.")
                # Retorna o status para o Orquestrador decidir
                return {"success": False, "reason": security_check["reason"], "status": "needs_confirmation"}

        # 3. Execução
        self.logger.info(f"Executando: '{command_to_execute}'")
        try:
            result = subprocess.run(
                command_to_execute,
                shell=True, check=True, capture_output=True, text=True, encoding='utf-8'
            )
            print("[USER] ✅ Comando executado com sucesso.")
            if result.stdout: print(f"--- Saída (stdout) ---\n{result.stdout}")
            if result.stderr: print(f"--- Erros (stderr) ---\n{result.stderr}")
            return {"success": True, "reason": "Executado com sucesso."}
        except subprocess.CalledProcessError as e:
            message = f"Erro ao executar o comando (código de saída: {e.returncode})."
            print(f"[USER] ❌ {message}")
            if e.stderr: print(f"--- Erros (stderr) ---\n{e.stderr}")
            self.logger.error(f"Erro de subprocesso ao executar '{command_to_execute}': {e.stderr}")
            return {"success": False, "reason": e.stderr}