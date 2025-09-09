# src/agents/frontend_agent.py

import os
from src.core.base_agent import BaseAgent
from src.core.logger import get_logger

FRONTEND_SYSTEM_PROMPT = """
Você é um Desenvolvedor Frontend Sênior, um especialista em criar interfaces de usuário (UI) bonitas, funcionais e responsivas.
Suas principais ferramentas são HTML5, CSS3 e JavaScript moderno (ES6+).
Você tem um olho aguçado para o design, focando em layouts limpos, excelente experiência do usuário (UX) e acessibilidade.
Sua tarefa é traduzir descrições de componentes de UI em um único arquivo HTML autocontido. O CSS e o JavaScript devem ser incluídos dentro do arquivo HTML usando as tags <style> e <script> para simplicidade.
Responda APENAS com o código HTML completo. Não inclua explicações ou texto extra fora do bloco de código.
"""

class FrontendAgent(BaseAgent):
    """
    Agente cognitivo que projeta e gera código de frontend (HTML, CSS, JS).
    """
    def __init__(self):
        super().__init__(
            agent_name="FrontendDev",
            system_prompt=FRONTEND_SYSTEM_PROMPT
        )
        self.logger = get_logger(self.agent_name)
        self.output_path = "workspace/output/frontend"
        os.makedirs(self.output_path, exist_ok=True)

    def run(self, description: str):
        """
        Gera o código de frontend com base em uma descrição e o salva em um arquivo.

        Args:
            description: Uma descrição em linguagem natural da UI a ser criada.
        """
        self.logger.info(f"Recebida tarefa de design: '{description[:50]}...'")
        
        try:
            # Usar o método think() da classe base para gerar o código
            html_code = self.think(description)

            # Limpeza básica caso o LLM adicione marcadores de markdown
            if html_code.strip().startswith("```html"):
                html_code = html_code.strip()[7:-3].strip()

            # Salvar o código gerado
            file_path = os.path.join(self.output_path, "index.html")
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(html_code)
            
            self.logger.info(f"Código de frontend gerado e salvo em: {file_path}")
            print(f"[USER] ✅ Design concluído! Verifique o arquivo em '{file_path}'")

        except Exception as e:
            self.logger.error(f"Erro ao gerar o design: {e}", exc_info=True)
            print(f"[USER] ❌ Erro durante o processo de design. Verifique 'logs/system_debug.log' para detalhes.")