# src/agents/architect_agent.py

import os
import time
from src.core.base_agent import BaseAgent

ARCHITECT_SYSTEM_PROMPT = """
Você é um Arquiteto de Software Sênior e Gerente de Projetos de IA. 
Sua função é receber um pedido de alto nível (de um usuário ou de um ticket de bug) e quebrá-lo em um plano de ação detalhado e estruturado.
O plano deve ser escrito em formato Markdown e salvo como 'plan.md' no workspace.

O plano deve conter:
1.  **Resumo do Projeto**: Uma breve descrição do que será construído ou corrigido.
2.  **Estrutura de Arquivos e Pastas**: Uma lista clara de todos os arquivos e diretórios a serem criados ou modificados.
3.  **Passos de Implementação Detalhados**: Uma sequência numerada de tarefas. Para modificações de arquivos, o plano deve incluir o conteúdo completo do novo arquivo.
4.  **Dependências**: Liste quaisquer bibliotecas ou pacotes que precisarão ser instalados.

Seja extremamente claro, preciso e não deixe espaço para ambiguidade. O Agente de Backend executará suas instruções literalmente.
"""

class ArchitectAgent(BaseAgent):
    """
    O agente que interpreta os pedidos, cria o plano de desenvolvimento
    e prioriza a correção de bugs.
    """
    def __init__(self):
        super().__init__(
            agent_name="Arquiteto",
            system_prompt=ARCHITECT_SYSTEM_PROMPT
        )
        self.user_request_file = "workspace/user_request.txt"
        self.bug_ticket_dir = "workspace/bugs"
        os.makedirs(self.bug_ticket_dir, exist_ok=True)

    def check_for_tasks(self):
        """Verifica se há tickets de bug ou solicitações de usuário."""
        # Prioridade 1: Tickets de Bug
        try:
            bug_tickets = [f for f in os.listdir(self.bug_ticket_dir) if f.endswith(".md")]
            if bug_tickets:
                ticket_path = os.path.join(self.bug_ticket_dir, bug_tickets[0])
                print(f"[{self.agent_name}] Ticket de bug encontrado: {bug_tickets[0]}")
                with open(ticket_path, 'r', encoding='utf-8') as f:
                    bug_description = f.read()
                
                os.remove(ticket_path)
                return f"Corrija o seguinte bug crítico: {bug_description}"
        except Exception as e:
            print(f"[{self.agent_name}] Erro ao verificar tickets de bug: {e}")

        # Prioridade 2: Solicitações do Usuário
        try:
            if os.path.exists(self.user_request_file):
                print(f"[{self.agent_name}] Solicitação de usuário encontrada.")
                with open(self.user_request_file, 'r', encoding='utf-8') as f:
                    user_request = f.read()
                
                os.remove(self.user_request_file)
                return f"Crie um plano de desenvolvimento para o seguinte pedido do usuário: '{user_request}'"
        except Exception as e:
            print(f"[{self.agent_name}] Erro ao verificar solicitações de usuário: {e}")
            
        return None

    def run(self, stop_event):
        """
        O loop principal do agente arquiteto.
        Verifica tarefas (bugs, solicitações) e cria planos de desenvolvimento.
        """
        print(f"[{self.agent_name}] Iniciando ciclo de planejamento...")
        while not stop_event.is_set():
            task_prompt = self.check_for_tasks()
            
            if task_prompt:
                development_plan = self.think(task_prompt)
                
                if development_plan and not development_plan.startswith("Erro:"):
                    self.write_to_workspace('plan.md', development_plan)
                    print(f"[{self.agent_name}] Plano de desenvolvimento criado para a tarefa.")
                else:
                    print(f"[{self.agent_name}] Não foi possível gerar um plano de desenvolvimento.")

            # Espera por 5 segundos, mas verifica o stop_event a cada segundo
            for _ in range(5):
                if stop_event.is_set():
                    break
                time.sleep(1)
        
        print(f"[{self.agent_name}] Ciclo de planejamento encerrado.")