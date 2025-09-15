# src/agents/architect_agent.py

import os
import time
import json
import re
from src.core.base_agent import BaseAgent
from src.core.logger import get_logger

ARCHITECT_SYSTEM_PROMPT = """
Você é um Arquiteto de Software Sênior. Sua função é receber uma solicitação e criar um plano de desenvolvimento em JSON.
Concentre-se em delegar tarefas de CODIFICAÇÃO para 'backend_dev' e 'frontend_dev' e tarefas de EXECUÇÃO DE COMANDOS para 'executor'.
NÃO crie tarefas que sejam apenas informativas ou de status (ex: "Não há tarefas de frontend"). Se um agente não tem trabalho a fazer, simplesmente não crie uma tarefa para ele.
NÃO crie tarefas para criar diretórios (`mkdir`) ou copiar arquivos (`cp`); a criação de arquivos e diretórios é uma consequência implícita das tarefas de codificação dos desenvolvedores.

Sua saída DEVE ser um único bloco de código JSON válido, e nada mais.
O JSON deve ter a seguinte estrutura:
{
  "project_id": "um-nome-unico-para-o-projeto",
  "description": "Um resumo do que será construído.",
  "action_plan": [
    {
      "agent": "backend_dev",
      "task": "Crie o arquivo 'main.py' com a lógica principal...",
      "target_file": "main.py"
    },
    {
      "agent": "backend_dev",
      "task": "Crie o arquivo 'requirements.txt' com as dependências.",
      "target_file": "requirements.txt"
    },
    {
      "agent": "executor",
      "task": "Instale as dependências do projeto.",
      "command": "pip install -r workspace/output/{project_id}/requirements.txt"
    }
  ]
}
Siga as regras do `project_map.md` fornecido no contexto.
"""

class ArchitectAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            agent_name="Arquiteto",
            system_prompt=ARCHITECT_SYSTEM_PROMPT
        )
        self.logger = get_logger(self.agent_name)
        self.project_map_path = "workspace/project_map.md"
        self.plans_queue_dir = "workspace/plans_queue"
        self.bug_dir = "workspace/bugs"
        os.makedirs(self.plans_queue_dir, exist_ok=True)
        os.makedirs(self.bug_dir, exist_ok=True)

    def _save_plan_to_queue(self, plan_json_str: str):
        try:
            if "```" in plan_json_str:
                plan_json_str = plan_json_str.split('```')[1].replace("json", "").strip()
            
            json.loads(plan_json_str)
            
            timestamp = int(time.time() * 1000)
            plan_filename = f"plan_{timestamp}.json"
            plan_path = os.path.join(self.plans_queue_dir, plan_filename)
            
            with open(plan_path, "w", encoding="utf-8") as f:
                f.write(plan_json_str)
            self.logger.info(f"Plano enfileirado com sucesso como '{plan_filename}'.")
        except (json.JSONDecodeError, IndexError) as e:
            self.logger.error(f"O Arquiteto gerou um JSON inválido: {e}\nJSON Recebido: {plan_json_str}")
            raise Exception("Arquiteto falhou em gerar um plano JSON válido.")

    def create_master_plan(self, user_request: str):
        self.logger.info(f"Criando plano mestre para: '{user_request[:50]}...'")
        try:
            with open(self.project_map_path, 'r', encoding='utf-8') as f:
                project_map_context = f.read()
        except FileNotFoundError:
            project_map_context = "Nenhum mapa de projeto encontrado."

        prompt_with_context = f"""
        **Contexto de Arquitetura (Regras a Seguir):**
        ---
        {project_map_context}
        ---
        **Solicitação do Usuário:**
        "{user_request}"
        Agora, gere o plano mestre completo em formato JSON para esta solicitação.
        """
        master_plan_json_str = self.think(prompt_with_context)
        if master_plan_json_str and not master_plan_json_str.startswith("Erro:"):
            self._save_plan_to_queue(master_plan_json_str)
        else:
            self.logger.error("Falha ao gerar o plano mestre.")
            raise Exception("Arquiteto falhou em gerar o plano mestre.")

    def create_correction_plan(self, ticket_file: str, bug_description: str):
        self.logger.info(f"Gerando plano de correção para o bug: {ticket_file}")
        correction_plan = None
        
        if ticket_file == "stale_plan.md":
            correction_plan = {
                "project_id": "system_maintenance",
                "description": "Plano de correção para remover um arquivo plan.md obsoleto.",
                "action_plan": [{"agent": "executor", "task": "Remover o arquivo workspace/plan.md obsoleto.", "command": "rm workspace/plan.md"}]
            }
        
        elif ticket_file == "orphan_projects.md":
            dirs_to_delete = re.findall(r"'([^']+)'", bug_description)
            if dirs_to_delete:
                commands = [f"rm -r workspace/output/{d}" for d in dirs_to_delete]
                full_command = " && ".join(commands)
                correction_plan = {
                    "project_id": "system_maintenance",
                    "description": "Limpar projetos órfãos do workspace.",
                    "action_plan": [{"agent": "executor", "task": f"Remover os seguintes diretórios órfãos: {', '.join(dirs_to_delete)}", "command": full_command}]
                }
        
        if correction_plan:
            self._save_plan_to_queue(json.dumps(correction_plan, indent=2))
        else:
            self.logger.warning(f"Lógica de correção para o bug '{ticket_file}' ainda não implementada.")

    def run(self, stop_event):
        self.logger.info("Arquiteto iniciando ciclo de monitoramento proativo de bugs...")
        while not stop_event.is_set():
            try:
                tickets = [f for f in os.listdir(self.bug_dir) if f.endswith(".md")]
                if tickets:
                    ticket_file = tickets[0]
                    ticket_path = os.path.join(self.bug_dir, ticket_file)
                    with open(ticket_path, 'r', encoding='utf-8') as f:
                        bug_description = f.read()
                    os.remove(ticket_path)
                    self.create_correction_plan(ticket_file, bug_description)
            except Exception as e:
                self.logger.error(f"Erro no ciclo de monitoramento de bugs do Arquiteto: {e}", exc_info=True)
            
            for _ in range(10):
                if stop_event.is_set(): break
                time.sleep(1)
        self.logger.info("Arquiteto encerrado.")