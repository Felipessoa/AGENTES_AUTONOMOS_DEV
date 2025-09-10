# src/core/orchestrator.py

import os
import shlex
import threading
import time
import queue

# Importando todos os agentes (PatcherAgent foi removido)
from src.agents.architect_agent import ArchitectAgent
from src.agents.backend_agent import BackendAgent
from src.agents.auditor_agent import AuditorAgent
from src.agents.git_agent import GitAgent
from src.agents.execution_agent import ExecutionAgent
from src.agents.compiler_agent import CompilerAgent
from src.agents.frontend_agent import FrontendAgent
from src.agents.prompt_engineer_agent import PromptEngineerAgent
# from src.agents.patcher_agent import PatcherAgent # <-- REMOVIDO

from src.core.logger import get_logger

logger = get_logger("Orchestrator")

class Orchestrator:
    """
    O cérebro do sistema. Gerencia o fluxo de trabalho de "Reescrita Segura".
    """
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
            # "patcher": PatcherAgent() # <-- REMOVIDO
        }
        self.stop_event = threading.Event()
        self.background_threads = []
        self.user_input_queue = queue.Queue()
        
        logger.info(f"Agentes carregados: {list(self.agents.keys())}")
        print("Orquestrador pronto.")

    def execute_backend_if_plan_exists(self):
        plan_ready_path = 'workspace/plan.ready'
        plan_path = 'workspace/plan.md'

        if os.path.exists(plan_ready_path):
            logger.info("Sinal 'plan.ready' detectado. Acionando Agente de Backend...")
            print("\n[USER] 🤖 Plano de ação autônomo detectado. Executando...")
            backend_dev = self.agents.get("backend")
            try:
                backend_dev.run()
                logger.info("Backend concluiu a execução do plano.")
                print("[USER] ✅ Plano executado com sucesso.")
            except Exception as e:
                logger.error(f"Erro durante a execução do Backend: {e}", exc_info=True)
                print(f"[USER] ❌ Erro ao executar o plano: {e}")
            finally:
                if os.path.exists(plan_path):
                    os.remove(plan_path)
                if os.path.exists(plan_ready_path):
                    os.remove(plan_ready_path)
            return True
        return False

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
        print("[USER] Passo 2/2: Plano enviado para a fila de execução.")

    def execute_modification_task(self, file_path: str, description: str):
        """
        Executa o ciclo de MODIFICAÇÃO usando a estratégia de Reescrita Segura.
        """
        print(f"\n[USER] Tarefa de modificação recebida para '{file_path}'.")
        
        prompt_engineer = self.agents.get("prompt_engineer")
        architect = self.agents.get("architect")
        backend = self.agents.get("backend") # <-- Usaremos o Backend

        try:
            # --- ETAPA 1: GERAR O NOVO CÓDIGO COMPLETO ---
            print("[USER] Passo 1/2: Arquiteto está planejando a modificação...")
            with open(file_path, 'r', encoding='utf-8') as f:
                existing_code = f.read()
            
            optimized_prompt = prompt_engineer.optimize_modification_prompt(file_path, existing_code, description)
            
            new_full_code = architect.generate_modified_code(optimized_prompt)
            logger.info(f"Novo código gerado para {file_path}.")

            # --- ETAPA 2: CRIAR PLANO DE REESCRITA E EXECUTAR ---
            print("[USER] Passo 2/2: Backend está aplicando a modificação...")
            
            # Cria um plano simples para o backend executar
            modification_plan = f"""
# Plano de Modificação para {file_path}
- **Ação:** Sobrescrever o arquivo `{file_path}` com o novo conteúdo.
- **Novo Conteúdo:**
"""
            architect.write_to_workspace('plan.md', modification_plan)
            # Sinaliza que o plano está pronto
            open("workspace/plan.ready", "w").close()
            logger.info("Plano de modificação enviado para a fila de execução.")

        except FileNotFoundError as e:
            print(f"[USER] ❌ Erro: {e}"); logger.error(f"Arquivo para modificar não encontrado: {file_path}"); return
        except Exception as e:
            print(f"[USER] ❌ Erro durante a modificação: {e}"); logger.error(f"Falha na modificação: {e}", exc_info=True); return
        
        # A mensagem de sucesso será impressa pelo loop principal quando o backend terminar.

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

    def _handle_user_input(self):
        """Função que roda em uma thread dedicada para capturar o input sem bloquear o loop principal."""
        while not self.stop_event.is_set():
            try:
                user_input = input("\nVocê> ")
                self.user_input_queue.put(user_input)
            except (EOFError, KeyboardInterrupt):
                self.stop_event.set()
                break

    def interactive_shell(self):
        self.start_background_agents()
        print("\n--- Shell de Orquestração Ativado ---")
        print("Fale comigo em linguagem natural. Para sair, digite 'exit' ou 'quit'.")
        
        input_thread = threading.Thread(target=self._handle_user_input, daemon=True)
        input_thread.start()

        prompt_engineer = self.agents.get("prompt_engineer")

        try:
            while not self.stop_event.is_set():
                self.execute_backend_if_plan_exists()
                
                try:
                    user_input = self.user_input_queue.get_nowait()
                    if user_input.lower() in ["exit", "quit"]:
                        print("Encerrando o Orquestrador..."); self.stop_event.set(); break
                    if not user_input: continue

                    analyzed_command = prompt_engineer.analyze_user_intent(user_input)
                    intent = analyzed_command.get("intent", "UNKNOWN").upper()
                    params = analyzed_command.get("params", {})

                    logger.info(f"Intenção detectada: {intent}, Parâmetros: {params}")

                    if intent == "BUILD":
                        if "description" in params: self.execute_creation_task(params["description"])
                        else: print("[USER] Para construir algo, preciso de uma descrição do que fazer.")
                    
                    elif intent == "MODIFY":
                        if "file_path" in params and "description" in params: self.execute_modification_task(params["file_path"], params["description"])
                        else: print("[USER] Para modificar um arquivo, preciso do caminho do arquivo e da descrição da mudança.")

                    elif intent == "DESIGN":
                        if "description" in params:
                            print("[USER] Tarefa de design recebida. Acionando FrontendAgent...")
                            self.agents.get("frontend").run(description=params["description"])
                        else: print("[USER] Para criar um design, preciso de uma descrição.")
                    
                    elif intent == "COMMIT":
                        if "commit_message" in params: self.agents.get("git").run(commit_message=params["commit_message"])
                        else: print("[USER] Para commitar, preciso de uma mensagem de commit.")
                    
                    elif intent == "RUN":
                        if "command_to_execute" in params: self.agents.get("executor").run(command_to_execute=params["command_to_execute"])
                        else: print("[USER] Para executar um comando, preciso saber qual comando rodar.")
                    
                    elif intent == "COMPILE":
                        if "script_path" in params: self.agents.get("compiler").run(script_path=params["script_path"])
                        else: print("[USER] Para compilar, preciso do caminho do script.")
                    
                    else:
                        print(f"[USER] Desculpe, não consegui entender sua solicitação. Tente reformular.")
                
                except queue.Empty:
                    pass
                
                time.sleep(0.5)
                
        except KeyboardInterrupt:
            print("\nEncerrando o Orquestrador (Ctrl+C)..."); self.stop_event.set()
        
        logger.info("Aguardando threads de segundo plano finalizem...")
        for thread in self.background_threads: thread.join(timeout=2)
        print("Sistema encerrado.")