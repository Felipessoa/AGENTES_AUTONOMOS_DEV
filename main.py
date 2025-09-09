# main.py

from dotenv import load_dotenv
from src.core.orchestrator import Orchestrator

def main():
    """
    Ponto de entrada principal do sistema.
    Carrega o ambiente e inicia o shell do Orquestrador.
    """
    load_dotenv()
    
    try:
        orchestrator = Orchestrator()
        orchestrator.interactive_shell()
        
    except Exception as e:
        print(f"Um erro fatal ocorreu na inicialização do sistema: {e}")

if __name__ == "__main__":
    main()