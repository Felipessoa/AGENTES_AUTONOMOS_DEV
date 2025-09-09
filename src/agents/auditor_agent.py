# src/agents/auditor_agent.py

import os
import time
from datetime import datetime, timedelta
from src.core.functional_agent import FunctionalAgent
from src.core.logger import get_logger

class AuditorAgent(FunctionalAgent):
    def __init__(self):
        super().__init__(agent_name="Auditor")
        self.logger = get_logger(self.agent_name)
        self.log_file = "logs/main_audit_log.txt"
        self.bug_dir = "workspace/bugs"
        os.makedirs(os.path.dirname(self.log_file), exist_ok=True)
        os.makedirs(self.bug_dir, exist_ok=True)

    def check_stale_plan(self):
        plan_path = "workspace/plan.md"
        if os.path.exists(plan_path):
            file_mod_time = datetime.fromtimestamp(os.path.getmtime(plan_path))
            if datetime.now() - file_mod_time > timedelta(minutes=2):
                bug_path = os.path.join(self.bug_dir, "stale_plan.md")
                if not os.path.exists(bug_path): # Evita criar tickets duplicados
                    self.logger.warning("Detectado 'plan.md' obsoleto. Criando ticket de bug.")
                    bug_content = "O arquivo plan.md está obsoleto (mais de 2 minutos) e pode indicar que um processo falhou. Recomenda-se a remoção ou investigação."
                    with open(bug_path, "w", encoding="utf-8") as f:
                        f.write(bug_content)

    def run(self, stop_event):
        self.logger.info("Iniciando monitoramento...")
        while not stop_event.is_set():
            # Lógica de verificação de bug
            self.check_stale_plan()

            # Lógica de log (pode ser removida se for muito barulhenta)
            # ...

            for _ in range(30): # Verifica a cada 30 segundos
                if stop_event.is_set():
                    break
                time.sleep(1)
        
        self.logger.info("Monitoramento encerrado.")