# main.py

from dotenv import load_dotenv
from src.core.orchestrator import Orchestrator
from src.core.logger import setup_logger
import logging

def main():
    """
    Ponto de entrada principal do sistema.
    """
    # Carrega as variáveis de ambiente do arquivo .env
    load_dotenv()
    
    # Configura o sistema de logging para todo o programa
    setup_logger()
    
    try:
        orchestrator = Orchestrator()
        orchestrator.interactive_shell()
        
    except Exception as e:
        # Usando o logger para registrar o erro fatal
        logging.getLogger("main").critical(f"Um erro fatal ocorreu na inicialização: {e}", exc_info=True)

if __name__ == "__main__":
    main()