# src/core/functional_agent.py

class FunctionalAgent:
    """
    Uma classe base para agentes funcionais.

    Esta classe serve como um modelo abstrato, garantindo que todas as subclasses
    forneçam uma implementação para o método 'run'.
    """

    def __init__(self, agent_name: str):
        """
        Inicializa o FunctionalAgent com um nome.

        Args:
            agent_name (str): O nome do agente, usado para identificação.
        """
        self.agent_name = agent_name

    def run(self):
        """
        O principal ponto de entrada para a lógica do agente.

        Este método deve ser sobrescrito por qualquer subclasse que herde
        de FunctionalAgent.

        Raises:
            NotImplementedError: Se a subclasse não implementar este método.
        """
        raise NotImplementedError("As subclasses devem implementar o método 'run'.")
