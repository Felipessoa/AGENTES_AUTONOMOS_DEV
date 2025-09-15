# src/agents/librarian_agent.py

import os
import time
import json
from src.core.functional_agent import FunctionalAgent
from src.core.logger import get_logger

class LibrarianAgent(FunctionalAgent):
    """
    Agente funcional que mantém um mapa da estrutura do projeto e um manifesto
    dos projetos gerados, servindo como uma fonte de verdade para outros agentes.
    """
    def __init__(self):
        super().__init__(agent_name="Librarian")
        self.logger = get_logger(self.agent_name)
        self.project_map_path = "workspace/project_map.md"
        self.manifest_path = "workspace/manifest.json"
        self.project_root = "."

    def _initialize_files(self):
        """Garante que o mapa e o manifesto existam."""
        if not os.path.exists(self.project_map_path):
            self.generate_project_map()
        if not os.path.exists(self.manifest_path):
            with open(self.manifest_path, 'w', encoding='utf-8') as f:
                json.dump({}, f, indent=4)
            self.logger.info(f"Manifesto de projetos inicializado em '{self.manifest_path}'")

    def generate_project_map(self):
        """
        Escaneia a estrutura do projeto e gera/atualiza o arquivo project_map.md.
        """
        self.logger.debug("Atualizando o mapa do projeto...")
        
        dir_map = {
            "src/core": "Contém os componentes centrais e a lógica de arquitetura do sistema (Orchestrator, BaseAgent). Regra: Apenas código de infraestrutura crítica.",
            "src/agents": "Contém a implementação de cada agente individual. Regra: Cada novo agente deve ter seu próprio arquivo aqui.",
            "workspace": "Diretório de trabalho para operações. Contém subpastas para artefatos gerados.",
            "workspace/output": "Diretório padrão para a saída de projetos gerados. Regra: Todos os novos projetos devem ser criados aqui.",
            "logs": "Contém todos os logs do sistema.",
            "Ambiente": "O sistema operacional é Linux (WSL). Use comandos de shell compatíveis (ex: `xdg-open`, `rm -r`). O comando `open` (macOS) não funcionará."
        }

        try:
            with open(self.project_map_path, "w", encoding="utf-8") as f:
                f.write("# Mapa do Projeto e Regras de Arquitetura\n\n")
                f.write("Este documento é a fonte da verdade sobre a estrutura do projeto. É mantido pelo LibrarianAgent.\n\n")
                
                for path, description in dir_map.items():
                    if path != "Ambiente":
                        full_path = os.path.join(self.project_root, path)
                        status = "✅ Encontrado" if os.path.isdir(full_path) else "❌ Não Encontrado"
                        f.write(f"### Diretório: `{path}` ({status})\n")
                    else:
                        f.write(f"### {path}\n")
                    f.write(f"- **Descrição/Regra:** {description}\n\n")
            
            self.logger.debug(f"Mapa do projeto atualizado com sucesso em '{self.project_map_path}'")
        except Exception as e:
            self.logger.error(f"Falha ao gerar o mapa do projeto: {e}", exc_info=True)

    def register_project_in_manifest(self, project_id: str, project_path: str, description: str):
        """Adiciona ou atualiza a entrada de um projeto no manifesto."""
        self.logger.info(f"Registrando projeto '{project_id}' no manifesto.")
        try:
            if not os.path.exists(self.manifest_path):
                manifest = {}
            else:
                with open(self.manifest_path, 'r', encoding='utf-8') as f:
                    manifest = json.load(f)
            
            manifest[project_id] = {
                "path": project_path,
                "description": description,
                "status": "ACTIVE",
                "created_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                "last_accessed": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
            }

            with open(self.manifest_path, 'w', encoding='utf-8') as f:
                json.dump(manifest, f, indent=4)

        except Exception as e:
            self.logger.error(f"Falha ao registrar projeto no manifesto: {e}", exc_info=True)

    def get_project_path(self, project_id: str, target_file: str) -> str:
        """
        Constrói o caminho absoluto e canônico para um arquivo de projeto.
        Esta é a única fonte da verdade para caminhos de projeto.
        """
        # A regra é que todos os projetos vão para workspace/output
        return os.path.abspath(os.path.join("workspace", "output", project_id, target_file))

    def run(self, stop_event):
        """
        Loop principal do agente. Atualiza o mapa do projeto periodicamente.
        """
        self.logger.info("Iniciando monitoramento da estrutura do projeto...")
        self._initialize_files()

        while not stop_event.is_set():
            self.generate_project_map()
            
            for _ in range(60):
                if stop_event.is_set():
                    break
                time.sleep(1)
        
        self.logger.info("Monitoramento da estrutura do projeto encerrado.")