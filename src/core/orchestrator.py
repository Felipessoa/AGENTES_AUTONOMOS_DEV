# src/core/orchestrator.py

import os
import shlex
import threading
import time
import diff_match_patch as dmp_module

from src.agents.architect_agent import ArchitectAgent
from src.agents.backend_agent import BackendAgent
from src.agents.auditor_agent import AuditorAgent
from src.agents.git_agent import GitAgent
from src.agents.execution_agent import ExecutionAgent
from src.agents.compiler_agent import CompilerAgent
from src.agents.frontend_agent import FrontendAgent
from src.agents.prompt_engineer_agent import PromptEngineerAgent
from src.agents.patcher_agent import PatcherAgent

from src.core.logger import get_logger

logger = get_logger("Orchestrator")

class Orchestrator:
    def __init__(self):
        logger.info("Inicializando o Orquestrador...")
        self.agents = {
            "architect": ArchitectAgent(),
            "backend": BackendAgent(project_root="."),
            "auditor": AuditorAgent(),
            "git": GitAgent(),
            "executor": ExecutionAgent(),
            "frontend": FrontendAgent(),
            "compiler": CompilerAgent(),
            "prompt_engineer": PromptEngineerAgent(),
            "patcher": PatcherAgent()
        }
        self.stop_event = threading.Event()
        self.background_threads = []
        
        logger.info(f"Agentes carregados: {list(self.agents.keys())}")
        print("Orquestrador pronto.")

    def execute_backend_if_plan_exists(self):
        """Verifica se um plano existe e, se sim, aciona o Backend."""
        if os.path.exists('workspace/plan.md'):
            logger.info("Plano detectado. Acionando Agente de Backend...")
            print("\n[USER] 🤖 Plano de ação detectado (criado por um agente). Executando...")
            backend_dev = self.agents.get("backend")
            try:
                backend_dev.run()
                logger.info("Backend concluiu a execução do plano.")
                print("[USER] ✅ Plano executado com sucesso.")
            except Exception as e:
                logger.error(f"Erro durante a execução do Backend: {e}", exc_info=True)
                print(f"[USER] ❌ Erro ao executar o plano: {e}")
            finally:
                # Limpa o plano após a execução para evitar re-execução
                if os.path.exists('workspace/plan.md'):
                    os.remove('workspace/plan.md')

    def execute_creation_task(self, task_prompt: str):
        print("\n[USER] Tarefa de construção recebida. Orquestrando agentes...")
        prompt_engineer = self.agents.get("prompt_engineer")
        architect = self.agents.get("architect")
        try:
            print("[USER] Passo 1/2: Engenheiro de Prompt e Arquiteto estão planejando...")
            optimized_prompt = prompt_engineer.optimize_creation_prompt(task_prompt)
            architect.plan_creation(optimized_prompt)
            logger.info("Plano de criação gerado com sucesso.")
        except Exception as e:
            print(f"[USER] ❌ Erro na etapa de planejamento: {e}")
            logger.error(f"Falha no planejamento da criação: {e}", exc_info=True)
            return
        
        # A execução do backend será pega pelo loop principal
        print("[USER] Passo 2/2: Plano enviado para a fila de execução.")


    def execute_modification_task(self, file_path: str, description: str):
        print(f"\n[USER] Tarefa de modificação recebida para '{file_path}'.")
        prompt_engineer = self.agents.get("prompt_engineer")
        architect = self.agents.get("architect")
        patcher = self.agents.get("patcher")
        try:
            print("[USER] Passo 1/3: Arquiteto está planejando a modificação...")
            with open(file_path, 'r', encoding='utf-8') as f:
                existing_code = f.read()
            optimized_prompt = prompt_engineer.optimize_modification_prompt(file_path, existing_code, description)
            new_full_code = architect.generate_modified_code(optimized_prompt)
            logger.info(f"Novo código gerado para {file_path}.")

            print("[USER] Passo 2/3: Gerando patch de modificação seguro...")
            dmp = dmp_module.diff_match_patch()
            patches = dmp.patch_make(existing_code, new_full_code)
            patch_text = dmp.patch_toText(patches)
            if not patch_text:
                print("[USER] ⚠️ O código gerado é idêntico ao original. Nenhuma modificação necessária.")
                return
            logger.info("Patch gerado com sucesso pelo Orquestrador.")

            print("[USER] Passo 3/3: Patcher está aplicando a modificação cirúrgica...")
            patcher.run(file_path=file_path, patch_content=patch_text)
            logger.info("Patcher concluiu a aplicação da modificação.")
        except FileNotFoundError as e:
            print(f"[USER] ❌ Erro: {e}"); logger.error(f"Arquivo para modificar não encontrado: {file_path}"); return
        except Exception as e:
            print(f"[USER] ❌ Erro na etapa de aplicação da modificação: {e}"); logger.error(f"Falha na aplicação do patch: {e}", exc_info=True); return
        
        print(f"[USER] ✅ Modificação de '{file_path}' concluída com sucesso!")

    def start_background_agents(self):
        logger.info("Iniciando agentes de segundo plano...")
        background_agent_keys = ["auditor", "architect"]
        for key in background_agent_keys:
            agent = self.agents.get(key)
            if agent:
                thread = threading.Thread(target=agent.run, args=(self.stop_event,), daemon=True)
                thread.start()
                self.background_threads.append(thread)
                logger.info(f"Agente '{agent.agent_name}' está rodando em segundo plano.")

    def interactive_shell(self):
        self.start_background_agents()
        print("\n--- Shell de Orquestração Ativado ---")
        print("Fale comigo em linguagem natural. Para sair, digite 'exit' ou 'quit'.")
        
        prompt_engineer = self.agents.get("prompt_engineer")

        try:
            while not self.stop_event.is_set():
                # O loop principal agora verifica por planos a cada ciclo
                self.execute_backend_if_plan_exists()
                
                user_input = input("\nVocê> ")
                if user_input.lower() in ["exit", "quit"]:
                    print("Encerrando o Orquestrador..."); self.stop_event.set(); break
                if not user_input: continue

                analyzed_command = prompt_engineer.analyze_user_intent(user_input)
                intent = analyzed_command.get("intent", "UNKNOWN").upper()
                params = analyzed_command.get("params", {})

                logger.info(f"Intenção detectada: {intent}, Parâmetros: {params}")

                if intent == "BUILD":
                    if "description" in params:
                        self.execute_creation_task(params["description"])
                    else:
                        print("[USER] Para construir algo, preciso de uma descrição do que fazer.")
                
                elif intent == "MODIFY":
                    if "file_path" in params and "description" in params:
                        self.execute_modification_task(params["file_path"], params["description"])
                    else:
                        print("[USER] Para modificar um arquivo, preciso do caminho do arquivo e da descrição da mudança.")

                elif intent == "DESIGN":
                    if "description" in params:
                        print("[USER] Tarefa de design recebida. Acionando FrontendAgent...")
                        self.agents.get("frontend").run(description=params["description"])
                    else:
                        print("[USER] Para criar um design, preciso de uma descrição.")

                elif intent == "COMMIT":
                    if "commit_message" in params:
                        self.agents.get("git").run(commit_message=params["commit_message"])
                    else:
                        print("[USER] Para commitar, preciso de uma mensagem de commit.")

                elif intent == "RUN":
                    if "command_to_execute" in params:
                        self.agents.get("executor").run(command_to_execute=params["command_to_execute"])
                    else:
                        print("[USER] Para executar um comando, preciso saber qual comando rodar.")

                elif intent == "COMPILE":
                    if "script_path" in params:
                        self.agents.get("compiler").run(script_path=params["script_path"])
                    else:
                        print("[USER] Para compilar, preciso do caminho do script.")

                else:
                    print(f"[USER] Desculpe, não consegui entender sua solicitação. Tente reformular.")
                
        except KeyboardInterrupt:
            print("\nEncerrando o Orquestrador (Ctrl+C)..."); self.stop_event.set()
        
        logger.info("Aguardando threads de segundo plano finalizem...")
        for thread in self.background_threads: thread.join(timeout=2)
        print("Sistema encerrado.")