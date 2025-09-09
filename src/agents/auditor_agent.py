# src/agents/auditor_agent.py

import os
import time
from datetime import datetime
from src.core.functional_agent import FunctionalAgent
from src.core.logger import get_logger

class AuditorAgent(FunctionalAgent):
    def __init__(self):
        super().__init__(agent_name="Auditor")
        self.logger = get_logger(self.agent_name)
        self.log_file = "logs/main_audit_log.txt"
        os.makedirs(os.path.dirname(self.log_file), exist_ok=True)

    def list_files(self, directory):
        try:
            return [f for f in os.listdir(directory) if os.path.isfile(os.path.join(directory, f))]
        except FileNotFoundError:
            return [f"Diretório '{directory}' não encontrado."]
        except Exception as e:
            return [f"Erro ao listar arquivos em '{directory}': {e}"]

    def run(self, stop_event):
        self.logger.info("Iniciando monitoramento...")
        while not stop_event.is_set():
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            workspace_files = self.list_files("workspace")
            agent_files = self.list_files("src/agents")
            
            workspace_files_str = "\n".join([f"  - {f}" for f in workspace_files])
            agent_files_str = "\n".join([f"  - {f}" for f in agent_files])

            audit_report = f"""--- Audit Log Entry: {timestamp} ---
Workspace Files:
{workspace_files_str}

Agent Files:
{agent_files_str}
--- End of Entry ---\n\n"""

            try:
                with open(self.log_file, "a", encoding="utf-8") as f:
                    f.write(audit_report)
                self.logger.debug("Auditoria concluída. Log atualizado.")
            except Exception as e:
                self.logger.error(f"Erro ao escrever no arquivo de log: {e}", exc_info=True)

            for _ in range(15):
                if stop_event.is_set():
                    break
                time.sleep(1)
        
        self.logger.info("Monitoramento encerrado.")