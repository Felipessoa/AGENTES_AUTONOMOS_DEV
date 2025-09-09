# workspace/src/core/logger.py
import logging

# Define um nível de log personalizado chamado USER com valor 25
# Este nível fica entre INFO (20) e WARNING (30)
USER_LEVEL_NUM = 25
logging.addLevelName(USER_LEVEL_NUM, "USER")

def setup_logger():
    """
    Configura o logger raiz do Python.
    
    Esta função deve ser chamada uma vez na inicialização da aplicação
    para garantir que todos os loggers subsequentes herdem esta configuração.
    """
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - [%(name)s] - %(message)s"
    )

def get_logger(name: str) -> logging.Logger:
    """
    Retorna uma instância de logger com o nome fornecido.

    Args:
        name (str): O nome do logger, geralmente __name__ do módulo chamador.

    Returns:
        logging.Logger: Uma instância do logger configurado.
    """
    return logging.getLogger(name)
