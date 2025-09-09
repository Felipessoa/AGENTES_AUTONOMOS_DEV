# src/core/logger.py

import logging
import sys
import os

def setup_logger():
    """
    Configura o logger raiz para o projeto.
    - INFO e acima irão para o console.
    - DEBUG e acima irão para um arquivo de log.
    """
    # Garante que o diretório de logs exista
    os.makedirs("logs", exist_ok=True)

    # Pega o logger raiz
    root_logger = logging.getLogger()
    
    # Evita adicionar manipuladores duplicados se a função for chamada novamente
    if root_logger.hasHandlers():
        root_logger.handlers.clear()

    root_logger.setLevel(logging.DEBUG) # O logger raiz captura tudo a partir de DEBUG

    # Cria um manipulador para o console (stdout)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO) # Apenas INFO, WARNING, ERROR, CRITICAL irão para o console
    
    # Cria um manipulador para o arquivo de log
    file_handler = logging.FileHandler("logs/system_debug.log", mode='a', encoding='utf-8')
    file_handler.setLevel(logging.DEBUG) # Todos os níveis irão para o arquivo de log

    # Define o formato do log
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - [%(name)s] - %(message)s')
    console_handler.setFormatter(formatter)
    file_handler.setFormatter(formatter)

    # Adiciona os manipuladores ao logger raiz
    root_logger.addHandler(console_handler)
    root_logger.addHandler(file_handler)

def get_logger(name: str) -> logging.Logger:
    """
    Retorna uma instância de um logger com o nome fornecido.
    """
    return logging.getLogger(name)