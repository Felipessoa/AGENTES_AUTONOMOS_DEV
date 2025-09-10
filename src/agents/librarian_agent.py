# src/agents/librarian_agent.py

import os
import time
from src.core.functional_agent import FunctionalAgent
from src.core.logger import get_logger

class LibrarianAgent(FunctionalAgent):
    """
    Agente funcional que mantém um mapa da estrutura do projeto,
    servindo como uma fonte de verdade para outros agentes.
    """
    def __init__(self):
        super().__init__(agent_name="Librarian")
        self.logger = get_logger(self.agent_name)
        self.project_map_path = "workspace/project_map.md"
        self.project_root = "." # Assume que a execução é da raiz do projeto

    def generate_project_map(self):
        """
        Escaneia a estrutura do projeto e gera/atualiza o arquivo project_map.md.
        """
        self.logger.info("Atualizando o mapa do projeto...")
        
        # Estrutura de diretórios e suas descrições
        dir_map = {
            "src/core": "Contém os componentes centrais e a lógica de arquitetura do sistema de agentes (Orchestrator, BaseAgent, etc.). Regra: Apenas código de infraestrutura crítica deve ser adicionado aqui.",
            "src/agents": "Contém a implementação de cada agente individual. Regra: Cada novo agente deve ter seu próprio arquivo aqui, herdando de BaseAgent ou FunctionalAgent.",
            "workspace": "Diretório de trabalho para operações. Contém subpastas para artefatos gerados.",
            "workspace/bugs": "Usado pelo AuditorAgent para criar tickets de bug. Regra: Arquivos aqui são priorizados pelo ArchitectAgent.",
            "workspace/output": "Diretório padrão para a saída de projetos gerados (ex: frontend, executáveis).",
            "logs": "Contém todos os logs do sistema, incluindo logs de debug detalhados."
        }

        try:
            with open(self.project_map_path, "w", encoding="utf-8") as f:
                f.write("# Mapa do Projeto e Regras de Arquitetura\n\n")
                f.write("Este documento é a fonte da verdade sobre a estrutura do projeto. Ele é mantido pelo LibrarianAgent.\n\n")
                
                for path, description in dir_map.items():
                    full_path = os.path.join(self.project_root, path)
                    status = "✅ Encontrado" if os.path.isdir(full_path) else "❌ Não Encontrado"
                    f.write(f"### Diretório: `{path}` ({status})\n")
                    f.write(f"- **Função:** {description}\n\n")
            
            self.logger.info(f"Mapa do projeto atualizado com sucesso em '{self.project_map_path}'")
        except Exception as e:
            self.logger.error(f"Falha ao gerar o mapa do projeto: {e}", exc_info=True)


    def run(self, stop_event):
        """
        Loop principal do agente. Atualiza o mapa do projeto periodicamente.
        """
        self.logger.info("Iniciando monitoramento da estrutura do projeto...")
        while not stop_event.is_set():
            self.generate_project_map()
            
            # Espera por 60 segundos
            for _ in range(60):
                if stop_event.is_set():
                    break
                time.sleep(1)
        
        self.logger.info("Monitoramento da estrutura do projeto encerrado.")