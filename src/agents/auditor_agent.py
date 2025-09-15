# src/agents/auditor_agent.py

import os
import time
import json
from datetime import datetime, timedelta
from src.core.functional_agent import FunctionalAgent
from src.core.logger import get_logger

class AuditorAgent(FunctionalAgent):
    """
    Agente de QA. Monitora a saúde do sistema, detecta anomalias
    e cria tickets de bug para problemas que precisam de atenção.
    """
    def __init__(self):
        super().__init__(agent_name="Auditor")
        self.logger = get_logger(self.agent_name)
        self.bug_dir = "workspace/bugs"
        self.manifest_path = "workspace/manifest.json"
        os.makedirs(self.bug_dir, exist_ok=True)

    def _create_bug_ticket(self, ticket_name: str, description: str):
        """Cria um ticket de bug se ele ainda não existir."""
        ticket_path = os.path.join(self.bug_dir, ticket_name)
        if not os.path.exists(ticket_path):
            self.logger.warning(f"Detectada anomalia! Criando ticket de bug: {ticket_name}")
            print(f"\n[USER] 🕵️ Auditor detectou um problema: {ticket_name}. Ticket criado.")
            try:
                with open(ticket_path, "w", encoding="utf-8") as f:
                    f.write(description)
            except Exception as e:
                self.logger.error(f"Falha ao criar ticket de bug {ticket_name}: {e}")
        else:
            self.logger.debug(f"Ticket de bug '{ticket_name}' já existe. Nenhuma ação necessária.")

    def audit_temporary_files(self):
        """Verifica se arquivos temporários (plan.md) estão obsoletos."""
        plan_path = "workspace/plan.md"
        if os.path.exists(plan_path):
            file_mod_time = datetime.fromtimestamp(os.path.getmtime(plan_path))
            if datetime.now() - file_mod_time > timedelta(minutes=5):
                self._create_bug_ticket(
                    "stale_plan.md",
                    "O arquivo plan.md está obsoleto (mais de 5 minutos) e pode indicar que um processo falhou ou travou. Recomenda-se a remoção."
                )

    def audit_workspace_orphans(self):
        """Verifica se há arquivos/pastas no workspace que não estão no manifesto."""
        try:
            if not os.path.exists(self.manifest_path):
                return

            with open(self.manifest_path, 'r', encoding='utf-8') as f:
                manifest = json.load(f)
            
            registered_paths = {os.path.basename(p['path']) for p in manifest.values()}
            
            output_dir = "workspace/output"
            if os.path.exists(output_dir):
                current_dirs = {d for d in os.listdir(output_dir) if os.path.isdir(os.path.join(output_dir, d))}
                
                orphan_dirs = current_dirs - registered_paths
                if orphan_dirs:
                    self._create_bug_ticket(
                        "orphan_projects.md",
                        f"Os seguintes diretórios de projeto existem em 'workspace/output' mas não estão registrados no manifesto: {', '.join(orphan_dirs)}. Eles podem ser resquícios de builds falhos e devem ser investigados ou limpos."
                    )
        except Exception as e:
            self.logger.error(f"Erro durante a auditoria de órfãos: {e}", exc_info=True)

    def run(self, stop_event):
        """
        Loop principal do agente. Roda auditorias periodicamente.
        """
        self.logger.info("Iniciando ciclo de auditoria de QA...")
        while not stop_event.is_set():
            self.logger.debug("Executando rotinas de auditoria...")
            self.audit_temporary_files()
            self.audit_workspace_orphans()
            
            for _ in range(120):
                if stop_event.is_set(): break
                time.sleep(1)
        
        self.logger.info("Ciclo de auditoria encerrado.")