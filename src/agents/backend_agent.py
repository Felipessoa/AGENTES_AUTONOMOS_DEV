# src/agents/backend_agent.py

import os
import subprocess
import json
from src.core.base_agent import BaseAgent
from src.core.logger import get_logger

BACKEND_SYSTEM_PROMPT = """
Você é um Agente Desenvolvedor de Backend Sênior. Sua única função é executar um plano de desenvolvimento fornecido a você.
Você receberá o conteúdo de um arquivo 'plan.md' em formato Markdown.
Sua tarefa é traduzir CADA passo do plano em uma sequência de comandos JSON.
Responda APENAS com um script JSON contendo uma lista de comandos. Não adicione explicações, comentários ou qualquer texto fora do bloco JSON. A sua saída deve ser um JSON puro e válido.
O formato preferencial é uma lista de objetos, cada um com as chaves "command" e "args". Ex: [{"command": "create_file", "args": {"path": "main.py", "content": "..."}}].
"""

class BackendAgent(BaseAgent):
    def __init__(self, project_root="."):
        super().__init__(
            agent_name="BackendDev",
            system_prompt=BACKEND_SYSTEM_PROMPT
        )
        self.logger = get_logger(self.agent_name)
        self.project_root = project_root
        self.logger.info(f"Operando no diretório raiz: '{os.path.abspath(self.project_root)}'")

    def _normalize_action(self, action: dict) -> tuple[str | None, dict | None]:
        """
        Aceita vários formatos de dicionário de ação e os converte para o formato padrão.
        Retorna (command, args) ou (None, None) se a normalização falhar.
        """
        if not isinstance(action, dict):
            return None, None

        # Converte todas as chaves para minúsculas para tratamento insensível a maiúsculas
        action_lower = {k.lower(): v for k, v in action.items()}

        # 1. Tenta o formato padrão: {"command": "...", "args": "..."}
        # Também aceita sinônimos como "action" e "parameters"
        command_key = "command" if "command" in action_lower else "action"
        args_key = "args" if "args" in action_lower else "parameters"
        
        if command_key in action_lower and args_key in action_lower:
            command = action_lower[command_key]
            args = action_lower[args_key]
            if isinstance(command, str) and isinstance(args, dict):
                return command, args

        # 2. Tenta o formato alternativo: {"create_file": {...}}
        if len(action_lower) == 1:
            command = list(action_lower.keys())[0]
            args = list(action_lower.values())[0]
            if isinstance(command, str) and isinstance(args, dict):
                return command, args

        # Se nenhum formato corresponder
        return None, None

    def _execute_actions(self, actions_json_str: str):
        try:
            if actions_json_str.strip().startswith("```json"):
                actions_json_str = actions_json_str.strip()[7:-3].strip()
            
            action_list = json.loads(actions_json_str)
            if not isinstance(action_list, list):
                self.logger.error(f"O JSON recebido não é uma lista: {actions_json_str}")
                raise TypeError("A resposta JSON do Backend LLM não foi uma lista de ações.")

            self.logger.info(f"Recebi {len(action_list)} ações para executar.")
            for i, action in enumerate(action_list, 1):
                
                # --- LÓGICA DE PARSING SUBSTITUÍDA PELA NORMALIZAÇÃO ---
                command, args = self._normalize_action(action)
                
                self.logger.debug(f"Ação normalizada {i}/{len(action_list)}: {command} com args {args}")

                if not command or not args:
                    self.logger.warning(f"Ação inválida ou em formato irreconhecível ignorada: {action}")
                    continue
                # --- FIM DA SUBSTITUIÇÃO ---

                if 'path' in args:
                    safe_relative_path = os.path.normpath(args['path']).lstrip('/\\')
                    absolute_path = os.path.join(self.project_root, safe_relative_path)
                    args['path'] = absolute_path
                    
                    if command in ["create_file", "append_to_file"]:
                        parent_dir = os.path.dirname(absolute_path)
                        if not os.path.exists(parent_dir):
                            os.makedirs(parent_dir)
                            self.logger.info(f"Criado diretório pai: {parent_dir}")

                if command == "create_directory":
                    os.makedirs(args['path'], exist_ok=True)
                    self.logger.info(f"Criado diretório: {args['path']}")
                
                elif command == "create_file":
                    with open(args['path'], 'w', encoding='utf-8') as f:
                        f.write(args.get('content', ''))
                    self.logger.info(f"Criado/Sobrescrito arquivo: {args['path']}")

                elif command == "append_to_file":
                    with open(args['path'], 'a', encoding='utf-8') as f:
                        f.write(args.get('content', ''))
                    self.logger.info(f"Adicionado conteúdo a: {args['path']}")

                elif command == "execute_shell":
                    self.logger.info(f"Executando no shell: '{args['command_line']}'")
                    subprocess.run(args['command_line'], shell=True, check=True, cwd=self.project_root, capture_output=True, text=True)
                
                else:
                    self.logger.warning(f"Comando normalizado desconhecido ignorado: {command}")

        except json.JSONDecodeError:
            self.logger.error(f"A resposta do LLM não é um JSON válido.\nResposta recebida:\n{actions_json_str}")
            raise ValueError("O LLM do Backend falhou em gerar um JSON válido.")
        except Exception as e:
            self.logger.error(f"Erro ao executar ação: {e}", exc_info=True)
            raise

    def run(self):
        self.logger.info(f"Agente de Backend ativado (Trabalhando em: {os.path.abspath(self.project_root)})")
        
        development_plan = self.read_from_workspace('plan.md')
        
        if not development_plan:
            self.logger.warning("'plan.md' não encontrado no workspace. Nada a fazer.")
            return

        self.logger.info("Plano de desenvolvimento encontrado. Traduzindo para ações executáveis...")
        
        actions_json_str = self.think(development_plan)
        
        if actions_json_str and not actions_json_str.startswith("Erro:"):
            self._execute_actions(actions_json_str)
        else:
            self.logger.error("Não foi possível traduzir o plano em ações.")
            raise Exception("O LLM do Backend falhou em traduzir o plano para JSON.")