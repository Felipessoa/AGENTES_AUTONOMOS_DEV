# src/agents/auditor_agent.py

import os
import time
from datetime import datetime
from src.core.base_agent import BaseAgent

# O system prompt pode ser simples, pois a lógica principal está no código Python.
AUDITOR_SYSTEM_PROMPT = "Você é um agente auditor. Sua função é observar o ambiente de desenvolvimento."

class AuditorAgent(BaseAgent):
    """
    O agente que monitora continuamente o estado do projeto,
    registrando atividades e mudanças.
    """
    def __init__(self):
        # Esta chamada é CRUCIAL. Ela inicializa a classe BaseAgent,
        # definindo self.agent_name, self.model, etc.
        super().__init__(
            agent_name="Auditor",
            system_prompt=AUDITOR_SYSTEM_PROMPT
        )

    def _list_files(self, startpath):
        """Helper para listar arquivos recursivamente em um diretório."""
        file_list = []
        for root, dirs, files in os.walk(startpath):
            # Ignora diretórios comuns para manter o log limpo
            if '__pycache__' in dirs:
                dirs.remove('__pycache__')
            if '.venv' in dirs:
                dirs.remove('.venv')
                
            for f in files:
                # Converte o caminho para ser relativo à raiz do projeto
                relative_path = os.path.relpath(os.path.join(root, f), '.')
                file_list.append(relative_path)
        return file_list

    def run(self):
        """
        O ponto de entrada principal para a lógica do agente.
        Executa um loop de monitoramento contínuo.
        """
        print(f"[{self.agent_name}] Iniciando o monitoramento em segundo plano...")
        
        while True:
            try:
                # 1. Obter a data e hora atual
                now = datetime.now()
                timestamp_str = now.strftime("%Y%m%d_%H%M%S")
                report_filename = f"audit_log_{timestamp_str}.txt"
                report_filepath = os.path.join('logs', report_filename)

                # 2. Listar arquivos nos diretórios de interesse
                agents_files = self._list_files('src/agents')
                workspace_files = self._list_files('workspace')

                # 3. Formatar o relatório
                report_content = f"Relatório de Auditoria - {now.strftime('%Y-%m-%d %H:%M:%S')}\n"
                report_content += "="*40 + "\n\n"
                
                report_content += "Arquivos de Agentes (src/agents):\n"
                report_content += "---------------------------------\n"
                if agents_files:
                    report_content += "\n".join(f"- {f}" for f in agents_files)
                else:
                    report_content += "Nenhum arquivo encontrado.\n"
                
                report_content += "\n\nArquivos do Workspace (workspace):\n"
                report_content += "-----------------------------------\n"
                if workspace_files:
                    report_content += "\n".join(f"- {f}" for f in workspace_files)
                else:
                    report_content += "Nenhum arquivo encontrado.\n"

                # 4. Escrever o relatório no arquivo de log
                # Garante que o diretório 'logs' exista
                os.makedirs('logs', exist_ok=True)
                with open(report_filepath, 'w', encoding='utf-8') as f:
                    f.write(report_content)

                # 5. Imprimir mensagem no console
                print(f"[{self.agent_name}] Auditoria concluída. Relatório salvo em '{report_filepath}'")

                # 6. Esperar por 15 segundos
                time.sleep(15)

            except Exception as e:
                print(f"[{self.agent_name}] Erro no loop de auditoria: {e}")
                # Espera mais tempo em caso de erro para evitar spam de logs
                time.sleep(60)