# src/agents/security_agent.py

# --- CORREÇÃO DE SINTAXE APLICADA AQUI ---
from src.core.functional_agent import FunctionalAgent
from src.core.logger import get_logger

class SecurityAgent(FunctionalAgent):
    """
    Agente funcional que analisa comandos para prevenir a execução de ações perigosas.
    """
    def __init__(self):
        super().__init__(agent_name="SecurityAgent")
        self.logger = get_logger(self.agent_name)
        # Lista de padrões que sempre exigirão confirmação do usuário
        self.confirmation_patterns = [
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

        Returns:
            Um dicionário com o status da análise e um motivo.
        """
        self.logger.debug(f"Analisando comando: '{command_string}'")
        command_lower = command_string.lower().strip()

        for pattern in self.confirmation_patterns:
            if pattern in command_lower:
                reason = f"Comando perigoso detectado (padrão: '{pattern}')."
                self.logger.warning(f"Comando requer confirmação: '{command_string}'. Motivo: {reason}")
                return {"status": "needs_confirmation", "reason": reason}

        self.logger.debug("Comando aprovado como seguro.")
        return {"status": "safe", "reason": "Comando parece seguro."}