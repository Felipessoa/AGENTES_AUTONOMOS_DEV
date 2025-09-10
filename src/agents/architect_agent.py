# src/agents/architect_agent.py

import os
import time
from src.core.base_agent import BaseAgent
from src.core.logger import get_logger

# --- SYSTEM PROMPT APRIMORADO ---
ARCHITECT_SYSTEM_PROMPT = """
Você é um Arquiteto de Software Sênior e executor de planos.
Sua função é receber um prompt e executá-lo fielmente.

Para CRIAÇÃO de novos arquivos, você gerará um plano em Markdown. Este plano DEVE seguir a seguinte estrutura:
1.  **Resumo do Projeto**: Breve descrição.
2.  **Estrutura de Arquivos**: Lista de todos os arquivos e pastas.
3.  **Conteúdo dos Arquivos**: O conteúdo completo para cada arquivo de código.
4.  **Gerenciamento de Dependências**: Esta etapa é OBRIGATÓRIA. Você DEVE incluir duas ações finais:
    a. A criação de um arquivo 'requirements.txt' listando todas as bibliotecas externas necessárias (ex: pygame, flask).
    b. Uma instrução explícita para o BackendAgent executar o comando `pip install -r requirements.txt` no diretório do projeto.

Para MODIFICAÇÃO de arquivos, você receberá o código atual e uma instrução, e sua tarefa é fornecer o NOVO código completo com a alteração aplicada, seguindo regras estritas.

Para CORREÇÃO DE BUGS, você gerará um plano em Markdown para resolver o problema descrito.

Sua resposta deve ser sempre o artefato solicitado, sem explicações adicionais.
"""

class ArchitectAgent(BaseAgent):
    """
    Agente proativo que prioriza a correção de bugs e depois lida com
    solicitações de usuário, gerando planos ou código modificado.
    """
    def __init__(self):
        super().__init__(
            agent_name="Arquiteto",
            system_prompt=ARCHITECT_SYSTEM_PROMPT
        )
        self.logger = get_logger(self.agent_name)
        self.bug_dir = "workspace/bugs"
        os.makedirs(self.bug_dir, exist_ok=True)

    def check_for_bugs(self):
        """Verifica e prioriza tickets de bug, criando um plano de correção."""
        try:
            tickets = [f for f in os.listdir(self.bug_dir) if f.endswith(".md")]
            if not tickets:
                return False

            ticket_file = tickets[0]
            ticket_path = os.path.join(self.bug_dir, ticket_file)
            self.logger.info(f"Ticket de bug encontrado! Priorizando a correção de: {ticket_file}")
            
            with open(ticket_path, 'r', encoding='utf-8') as f:
                bug_description = f.read()
            
            os.remove(ticket_path)
            
            if ticket_file == "stale_plan.md":
                self.logger.info("Gerando plano de correção para 'stale_plan.md'.")
                correction_plan = """
# Plano de Correção para plan.md Obsoleto
## 1. Executar Comando de Limpeza
- **Ação:** Executar um comando de shell para remover o arquivo obsoleto.
- **Agente Responsável:** BackendAgent
## Detalhes da Ação
O BackendAgent deve traduzir a seguinte instrução para um comando JSON `execute_shell`: `rm workspace/plan.md`
"""
                self.write_to_workspace('plan.md', correction_plan)
                open("workspace/plan.ready", "w").close()
                return True
            else:
                self.logger.warning(f"Lógica de correção para o bug '{ticket_file}' ainda não implementada.")
                return False

        except Exception as e:
            self.logger.error(f"Erro ao verificar tickets de bug: {e}", exc_info=True)
            return False

    def plan_creation(self, optimized_prompt: str):
        """Cria um plano em Markdown para um NOVO artefato."""
        self.logger.info("Recebido prompt otimizado para criação...")
        development_plan = self.think(optimized_prompt)
        if development_plan and not development_plan.startswith("Erro:"):
            self.write_to_workspace('plan.md', development_plan)
            open("workspace/plan.ready", "w").close()
            self.logger.info("Plano de criação gerado e sinalizado como pronto.")
        else:
            raise Exception("Arquiteto falhou em gerar um plano de criação a partir do prompt otimizado.")

    def generate_modified_code(self, optimized_prompt: str) -> str:
        """Gera e retorna o texto do código modificado a partir de um prompt otimizado."""
        self.logger.info("Recebido prompt otimizado para gerar código modificado...")
        new_full_code = self.think(optimized_prompt)
        if new_full_code and not new_full_code.startswith("Erro:"):
            if "```" in new_full_code:
                parts = new_full_code.split('```')
                if len(parts) > 1:
                    new_full_code = parts[1]
                    first_line, *rest_of_lines = new_full_code.split('\n')
                    if first_line.lower().strip() in ['python', 'py']:
                        new_full_code = '\n'.join(rest_of_lines)
                    else:
                        new_full_code = '\n'.join([first_line] + rest_of_lines)
                    new_full_code = new_full_code.strip()
            self.logger.info("Código modificado gerado com sucesso.")
            return new_full_code
        else:
            raise Exception("Arquiteto falhou em gerar o código modificado a partir do prompt otimizado.")

    def run(self, stop_event):
        """Loop principal do agente Arquiteto. Roda em segundo plano para monitorar bugs."""
        self.logger.info("Iniciando ciclo de monitoramento proativo...")
        while not stop_event.is_set():
            self.logger.debug("Verificando por tarefas de bug...")
            self.check_for_bugs()
            for _ in range(10):
                if stop_event.is_set():
                    break
                time.sleep(1)
        self.logger.info("Ciclo de monitoramento do Arquiteto encerrado.")