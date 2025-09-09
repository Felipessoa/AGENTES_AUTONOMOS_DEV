# src/core/logger.py

import logging
import sys

# Define um novo nível de log para feedback direto ao usuário
USER_LEVEL_NUM = 25
logging.addLevelName(USER_LEVEL_NUM, "USER")

def user(self, message, *args, **kws):
    if self.isEnabledFor(USER_LEVEL_NUM):
        self._log(USER_LEVEL_NUM, message, args, **kws)

logging.Logger.user = user

def setup_logger():
    """
    Configura o logger raiz para o projeto.
    - INFO e acima irão para o console.
    - DEBUG e acima irão para um arquivo de log.
    """
    # Cria um manipulador para o console (stdout)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO) # Apenas INFO, USER, WARNING, ERROR, CRITICAL irão para o console
    
    # Cria um manipulador para o arquivo de log
    file_handler = logging.FileHandler("logs/system_debug.log", mode='a', encoding='utf-8')
    file_handler.setLevel(logging.DEBUG) # Todos os níveis irão para o arquivo de log

    # Define o formato do log
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - [%(name)s] - %(message)s')
    console_handler.setFormatter(formatter)
    file_handler.setFormatter(formatter)

    # Pega o logger raiz e adiciona os manipuladores
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG) # O logger raiz captura tudo a partir de DEBUG
    
    # Evita adicionar manipuladores duplicados se a função for chamada novamente
    if not root_logger.handlers:
        root_logger.addHandler(console_handler)
        root_logger.addHandler(file_handler)

def get_logger(name: str) -> logging.Logger:
    """
    Retorna uma instância de um logger com o nome fornecido.
    """
    return logging.getLogger(name)