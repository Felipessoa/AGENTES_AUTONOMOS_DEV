# src/agents/architect_agent.py

from src.core.base_agent import BaseAgent
from src.core.logger import get_logger

ARCHITECT_SYSTEM_PROMPT = """
Você é um Arquiteto de Software Sênior e executor de planos.
Sua função é receber um prompt extremamente detalhado e otimizado e executá-lo fielmente.
Para CRIAÇÃO de novos arquivos, você gerará um plano em Markdown.
Para MODIFICAÇÃO de arquivos, você gerará um patch no formato diff unificado.
Sua resposta deve ser sempre o artefato solicitado, sem explicações adicionais.
"""

class ArchitectAgent(BaseAgent):
    """
    O agente que recebe prompts otimizados e gera os planos de desenvolvimento
    ou os patches de modificação.
    """
    def __init__(self):
        super().__init__(
            agent_name="Arquiteto",
            system_prompt=ARCHITECT_SYSTEM_PROMPT
        )
        self.logger = get_logger(self.agent_name)

    def plan_creation(self, optimized_prompt: str):
        """Cria um plano para um NOVO artefato a partir de um prompt otimizado."""
        self.logger.info("Recebido prompt otimizado para criação...")
        
        development_plan = self.think(optimized_prompt)
        
        if development_plan and not development_plan.startswith("Erro:"):
            self.write_to_workspace('plan.md', development_plan)
            self.logger.info("Plano de criação gerado com sucesso.")
        else:
            raise Exception("Arquiteto falhou em gerar um plano de criação a partir do prompt otimizado.")

    def plan_modification(self, optimized_prompt: str, file_path: str):
        """
        Gera um patch a partir de um prompt otimizado e o salva em um arquivo.
        """
        self.logger.info(f"Recebido prompt otimizado para gerar patch para: {file_path}")

        patch_content = self.think(optimized_prompt)
        
        if patch_content and not patch_content.startswith("Erro:"):
            # Limpa o conteúdo de possíveis blocos de código
            if "```" in patch_content:
                parts = patch_content.split('```')
                if len(parts) > 1:
                    patch_content = parts[1]
                    # Remove a linguagem (ex: 'diff', 'patch') do início
                    if patch_content.lower().startswith(('diff', 'patch')):
                        patch_content = '\n'.join(patch_content.split('\n')[1:])
                    patch_content = patch_content.strip()
            
            # Salva o patch em um arquivo, não um plano
            self.write_to_workspace('modification.patch', patch_content)
            self.logger.info(f"Patch para {file_path} gerado com sucesso.")
        else:
            raise Exception("Arquiteto falhou em gerar o patch a partir do prompt otimizado.")

    def run(self, stop_event):
        """O Arquiteto é puramente reativo e não precisa de um loop de fundo."""
        pass