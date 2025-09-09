# src/agents/architect.py

from src.core.base_agent import BaseAgent

# A "personalidade" e as diretrizes do nosso agente arquiteto.
# Este é um dos pontos mais importantes para a qualidade do resultado.
ARCHITECT_SYSTEM_PROMPT = """
Você é um Arquiteto de Software Sênior e Gerente de Projetos de IA. 
Sua função é receber um pedido de alto nível de um usuário e quebrá-lo em um plano de ação detalhado e estruturado.
O plano deve ser escrito em formato Markdown e salvo como 'plan.md' no workspace.

O plano deve conter:
1.  **Resumo do Projeto**: Uma breve descrição do que será construído.
2.  **Estrutura de Arquivos e Pastas**: Uma lista clara de todos os arquivos e diretórios a serem criados.
3.  **Passos de Implementação Detalhados**: Uma sequência numerada de tarefas. Cada tarefa deve ser específica, acionável e atribuída a um agente (ex: "BACKEND_DEV: Crie o arquivo 'main.py' com o seguinte código...").
4.  **Dependências**: Liste quaisquer bibliotecas ou pacotes que precisarão ser instalados.

Seja extremamente claro, preciso e não deixe espaço para ambiguidade. O Agente de Backend executará suas instruções literalmente.
"""

class ArchitectAgent(BaseAgent):
    """
    O agente que interage com o usuário, interpreta os pedidos
    e cria o plano de desenvolvimento.
    """
    def __init__(self):
        super().__init__(
            agent_name="Arquiteto",
            system_prompt=ARCHITECT_SYSTEM_PROMPT
        )

    def run(self):
        """
        Inicia o loop de interação com o usuário.
        """
        print("\n--- Agente Arquiteto Ativado ---")
        print("Qual software você gostaria de construir hoje?")
        
        try:
            user_request = input("Você: ")
            
            if not user_request:
                print("[Arquiteto] Nenhum pedido recebido. Encerrando.")
                return

            # O prompt que será enviado para o LLM pensar
            prompt_for_llm = f"Crie um plano de desenvolvimento detalhado para o seguinte pedido do usuário: '{user_request}'"
            
            # Usa o método think() da classe base para obter o plano
            development_plan = self.think(prompt_for_llm)
            
            # Salva o plano no workspace para outros agentes
            if development_plan and not development_plan.startswith("Erro:"):
                self.write_to_workspace('plan.md', development_plan)
                print("[Arquiteto] Plano de desenvolvimento criado e salvo em 'workspace/plan.md'.")
            else:
                print("[Arquiteto] Não foi possível gerar um plano de desenvolvimento.")

        except KeyboardInterrupt:
            print("\n[Arquiteto] Operação interrompida pelo usuário. Encerrando.")
        except Exception as e:
            print(f"[Arquiteto] Um erro inesperado ocorreu: {e}")