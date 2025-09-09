# src/core/functional_agent.py

class FunctionalAgent:
    """
    Classe base para todos os agentes funcionais (determinísticos).
    """
    def __init__(self, agent_name: str):
        self.agent_name = agent_name

    def run(self, **kwargs):
        """
        O ponto de entrada principal para a lógica do agente.
        Este método deve ser sobrescrito por cada agente filho.
        """
        raise NotImplementedError(f"O método 'run' deve ser implementado pela subclasse {self.__class__.__name__}.")