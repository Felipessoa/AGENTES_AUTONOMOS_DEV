# src/agents/backend_agent.py

import os
import subprocess
import json
from src.core.base_agent import BaseAgent

# A "personalidade" e as diretrizes do nosso agente de backend.
# Ele é focado em traduzir planos em ações de sistema de arquivos.
BACKEND_SYSTEM_PROMPT = """
Você é um Agente Desenvolvedor de Backend Sênior. Sua única função é executar um plano de desenvolvimento fornecido a você.
Você receberá o conteúdo de um arquivo 'plan.md'.
Sua tarefa é traduzir CADA passo do plano em uma sequência de comandos executáveis: comandos de terminal (como mkdir, touch) e blocos de código para serem escritos em arquivos.

Responda APENAS com um script JSON contendo uma lista de comandos. Não adicione explicações, comentários ou qualquer texto fora do bloco JSON. A sua saída deve ser um JSON puro e válido.

O formato JSON deve ser uma lista de objetos, onde cada objeto tem "command" e "args".
Comandos válidos são: "create_directory", "create_file", "append_to_file", "execute_shell".

Exemplo de saída JSON para um plano simples:
[
  {
    "command": "create_directory",
    "args": {
      "path": "src/app"
    }
  },
  {
    "command": "create_file",
    "args": {
      "path": "src/app/main.py",
      "content": "def hello_world():\\n    print('Hello, World!')\\n\\nif __name__ == '__main__':\\n    hello_world()"
    }
  },
  {
    "command": "execute_shell",
    "args": {
      "command_line": "pip install flask"
    }
  }
]
Traduza o plano fornecido em um JSON como este. Seja literal e preciso.
"""

class BackendAgent(BaseAgent):
    """
    O agente que lê o plano de desenvolvimento e executa as
    ações de criação de arquivos e escrita de código.
    """
    def __init__(self, project_root="workspace/generated_project"):
        super().__init__(
            agent_name="BackendDev",
            system_prompt=BACKEND_SYSTEM_PROMPT
        )
        # O diretório onde o código do projeto será gerado
        self.project_root = project_root
        if not os.path.exists(self.project_root) and self.project_root != ".":
            os.makedirs(self.project_root)
        print(f"[{self.agent_name}] Operando no diretório raiz: '{os.path.abspath(self.project_root)}'")

    def _execute_actions(self, actions_json_str: str):
        """
        Processa a string JSON de ações e as executa no sistema de arquivos.
        """
        try:
            # Limpa o JSON de possíveis blocos de código markdown que o LLM pode adicionar
            if actions_json_str.strip().startswith("```json"):
                actions_json_str = actions_json_str.strip()[7:-3].strip()
            
            action_list = json.loads(actions_json_str)
            if not isinstance(action_list, list):
                print(f"[{self.agent_name}] Erro: O JSON recebido não é uma lista.")
                return

            print(f"[{self.agent_name}] Recebi {len(action_list)} ações para executar.")
            for i, action in enumerate(action_list, 1):
                command = action.get("command")
                args = action.get("args")

                print(f"  Ação {i}/{len(action_list)}: {command}")

                if not command or not args:
                    print(f"    - Ação inválida ignorada: {action}")
                    continue

                # Garante que todos os caminhos sejam relativos ao root do projeto
                if 'path' in args:
                    # Previne ataques de travessia de diretório (Path Traversal)
                    # normpath limpa caminhos como 'src/../src/agents' para 'src/agents'
                    # lstrip remove barras iniciais para evitar que seja tratado como caminho absoluto
                    safe_relative_path = os.path.normpath(args['path']).lstrip('/\\')
                    absolute_path = os.path.join(self.project_root, safe_relative_path)
                    args['path'] = absolute_path
                    
                    # Garante que o diretório pai exista antes de criar um arquivo
                    if command in ["create_file", "append_to_file"]:
                        parent_dir = os.path.dirname(absolute_path)
                        if not os.path.exists(parent_dir):
                            os.makedirs(parent_dir)
                            print(f"    - Criado diretório pai: {parent_dir}")

                if command == "create_directory":
                    os.makedirs(args['path'], exist_ok=True)
                    print(f"    - Criado diretório: {args['path']}")
                
                elif command == "create_file":
                    with open(args['path'], 'w', encoding='utf-8') as f:
                        f.write(args.get('content', ''))
                    print(f"    - Criado arquivo: {args['path']}")

                elif command == "append_to_file":
                    with open(args['path'], 'a', encoding='utf-8') as f:
                        f.write(args.get('content', ''))
                    print(f"    - Adicionado conteúdo a: {args['path']}")

                elif command == "execute_shell":
                    print(f"    - Executando no shell: '{args['command_line']}'")
                    # Executa o comando dentro do diretório raiz do projeto
                    subprocess.run(args['command_line'], shell=True, check=True, cwd=self.project_root)
                
                else:
                    print(f"    - Comando desconhecido ignorado: {command}")

        except json.JSONDecodeError:
            print(f"[{self.agent_name}] Erro: A resposta do LLM não é um JSON válido.")
            print(f"Resposta recebida (primeiros 500 caracteres):\n{actions_json_str[:500]}")
        except Exception as e:
            print(f"[{self.agent_name}] Erro ao executar ação: {e}")

    def run(self):
        """
        Ponto de entrada do agente. Lê o plano e o executa.
        """
        print(f"\n--- Agente de Backend Ativado (Trabalhando em: {os.path.abspath(self.project_root)}) ---")
        
        development_plan = self.read_from_workspace('plan.md')
        
        if not development_plan:
            print("[BackendDev] 'plan.md' não encontrado no workspace. Nada a fazer. Encerrando.")
            return

        print("[BackendDev] Plano de desenvolvimento encontrado. Traduzindo para ações executáveis...")
        
        # Usa o método think() para converter o plano em um JSON de ações
        actions_json_str = self.think(development_plan)
        
        if actions_json_str and not actions_json_str.startswith("Erro:"):
            self._execute_actions(actions_json_str)
            print("[BackendDev] Execução do plano concluída.")
        else:
            print("[BackendDev] Não foi possível traduzir o plano em ações.")