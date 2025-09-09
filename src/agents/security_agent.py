# src/agents/security_agent.py

from src.core.functional_agent import FunctionalAgent
from src.core.logger import get_logger

class SecurityAgent(FunctionalAgent):
    """
    Agente funcional que analisa comandos para prevenir a execução de ações perigosas.
    """
    def __init__(self):
        super().__init__(agent_name="SecurityAgent")
        self.logger = get_logger(self.agent_name)
        # Lista de padrões de comandos perigosos. Pode ser expandida.
        self.dangerous_patterns = [
            "rm -rf",
            "sudo",
            "mv /",
            "dd ",
            ":(){:|:&};:", # Fork bomb
            "mkfs",
            "> /dev/sd"
        ]

    def analyze_command(self, command_string: str) -> dict:
        """
        Verifica um comando contra uma lista de padrões perigosos.

        Args:
            command_string: O comando a ser analisado.

        Returns:
            Um dicionário com o status da aprovação e um motivo.
        """
        self.logger.debug(f"Analisando comando: '{command_string}'")
        command_lower = command_string.lower().strip()

        for pattern in self.dangerous_patterns:
            if pattern in command_lower:
                reason = f"Comando perigoso detectado (padrão: '{pattern}')."
                self.logger.warning(f"Bloqueado comando perigoso: '{command_string}'. Motivo: {reason}")
                return {"approved": False, "reason": reason}

        self.logger.debug("Comando aprovado como seguro.")
        return {"approved": True, "reason": "Comando parece seguro."}

    def run(self):
        """Este agente não é executado diretamente por um comando do usuário."""
        self.logger.info("SecurityAgent não possui uma ação 'run' direta. Ele é chamado por outros agentes.")
        pass