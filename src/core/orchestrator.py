# src/core/orchestrator.py

import os
import shlex
import threading
import time
import queue
import json

from src.agents.architect_agent import ArchitectAgent
from src.agents.backend_agent import BackendAgent
from src.agents.auditor_agent import AuditorAgent
from src.agents.execution_agent import ExecutionAgent
from src.agents.librarian_agent import LibrarianAgent
from src.agents.prompt_engineer_agent import PromptEngineerAgent
from src.agents.git_agent import GitAgent
from src.agents.compiler_agent import CompilerAgent
from src.agents.frontend_agent import FrontendAgent
from src.agents.security_agent import SecurityAgent

from src.core.logger import get_logger

logger = get_logger("Orchestrator")

class Orchestrator:
    """
    Orquestrador v3.3. Lógica de caminhos centralizada no LibrarianAgent.
    """
    def __init__(self):
        logger.info("Inicializando o Orquestrador v3.3...")
        self.agents = {
            "architect": ArchitectAgent(),
            "backend_dev": BackendAgent(),
            "auditor": AuditorAgent(),
            "executor": ExecutionAgent(),
            "librarian": LibrarianAgent(),
            "prompt_engineer": PromptEngineerAgent(),
            "git": GitAgent(),
            "compiler": CompilerAgent(),
            "frontend_dev": FrontendAgent(),
        }
        self.stop_event = threading.Event()
        self.background_threads = []
        self.user_input_queue = queue.Queue()
        self.project_in_progress = threading.Event()
        self.prompt_needed = threading.Event()

        logger.info(f"Agentes carregados: {list(self.agents.keys())}")
        print("Orquestrador pronto.")

    def process_plan_queue(self):
        plans_queue_dir = "workspace/plans_queue"
        if not os.path.exists(plans_queue_dir): return

        plans = sorted([f for f in os.listdir(plans_queue_dir) if f.endswith(".json")])
        if not plans: return

        self.project_in_progress.set()
        plan_filename = plans[0]
        plan_path = os.path.join(plans_queue_dir, plan_filename)
        
        logger.info(f"Plano '{plan_filename}' detectado na fila. Iniciando execução...")
        print(f"\n[USER] 🤖 Plano de ação '{plan_filename}' detectado. Executando...")

        plan_succeeded = True
        project_id = "unknown_project"
        project_description = "N/A"

        try:
            with open(plan_path, 'r', encoding='utf-8') as f:
                plan = json.load(f)

            project_id = plan.get("project_id", "unknown_project")
            project_description = plan.get("description", "N/A")
            tasks = plan.get("action_plan", [])
            
            if not tasks:
                logger.warning(f"Plano '{plan_filename}' encontrado, mas sem tarefas.")
                print(f"[USER] ⚠️ Plano '{plan_filename}' encontrado, mas não continha tarefas claras.")
                return

            total_tasks = len(tasks)
            for i, task in enumerate(tasks, 1):
                agent_name = task.get("agent", "").lower()
                task_description = task.get("task", "")
                
                print(f"\n[USER] Executando Tarefa {i}/{total_tasks}: Atribuída a '{agent_name}'")
                print(f"[USER] Descrição: {task_description}")
                
                agent = self.agents.get(agent_name)
                if not agent:
                    logger.error(f"Agente '{agent_name}' especificado no plano não encontrado.")
                    print(f"[USER] ❌ Erro: Agente '{agent_name}' não existe no sistema.")
                    plan_succeeded = False
                    continue

                try:
                    if agent_name in ["backend_dev", "frontend_dev"]:
                        target_file = task.get("target_file")
                        if not target_file:
                            logger.warning(f"Tarefa para '{agent_name}' sem 'target_file', pulando: {task_description}")
                            print(f"[USER] ⚠️ Tarefa informativa para '{agent_name}' ignorada.")
                            continue
                        
                        # --- LÓGICA DE CAMINHO DELEGADA AO BIBLIOTECÁRIO ---
                        librarian = self.agents.get("librarian")
                        final_path = librarian.get_project_path(project_id, target_file)
                        
                        agent.write_code(file_path=final_path, task_description=task_description)
                    
                    elif agent_name == "executor":
                        command = task.get("command")
                        if not command: raise ValueError("A tarefa do executor precisa de um 'command'.")
                        command = command.replace("{project_id}", project_id)
                        agent.run(command_to_execute=command)
                    
                    else:
                        logger.warning(f"Lógica de execução para o agente '{agent_name}' não implementada.")
                        print(f"[USER] ⚠️ Lógica para o agente '{agent_name}' não implementada.")

                except Exception as e:
                    print(f"[USER] ❌ Erro ao executar a tarefa {i}: {e}")
                    logger.error(f"Falha na tarefa '{task_description}': {e}", exc_info=True)
                    plan_succeeded = False
                    break

            if plan_succeeded:
                print(f"\n[USER] ✅ Todas as tarefas do plano '{plan_filename}' foram processadas com sucesso.")
                if project_id != "system_maintenance":
                    librarian = self.agents.get("librarian")
                    project_path = os.path.join("workspace", "output", project_id)
                    librarian.register_project_in_manifest(project_id, project_path, project_description)
            else:
                print(f"\n[USER] ❌ O plano '{plan_filename}' foi processado com erros.")

        except Exception as e:
            logger.error(f"Erro durante a execução do plano '{plan_filename}': {e}", exc_info=True)
            print(f"[USER] ❌ Erro crítico ao executar o plano de projeto '{plan_filename}': {e}")
        finally:
            if os.path.exists(plan_path):
                os.remove(plan_path)
            self.project_in_progress.clear()
            self.prompt_needed.set()

    def start_background_agents(self):
        logger.info("Iniciando agentes de segundo plano...")
        background_agent_keys = ["librarian", "auditor", "architect"]
        for key in background_agent_keys:
            agent = self.agents.get(key)
            if agent:
                thread = threading.Thread(target=agent.run, args=(self.stop_event,), daemon=True)
                thread.start()
                self.background_threads.append(thread)
                logger.info(f"Agente '{agent.agent_name}' está rodando em segundo plano.")

    def _handle_user_input(self):
        while not self.stop_event.is_set():
            try:
                user_input = input()
                if self.stop_event.is_set(): break
                self.user_input_queue.put(user_input)
            except (EOFError, RuntimeError):
                self.logger.info("Input stream fechado ou interrompido. Sinalizando encerramento.")
                self.stop_event.set(); break

    def interactive_shell(self):
        self.start_background_agents()
        print("\n--- Shell de Orquestração v3.3 (Estável) Ativado ---")
        print("Descreva o projeto que você quer construir.")
        
        input_thread = threading.Thread(target=self._handle_user_input, daemon=True)
        input_thread.start()

        architect = self.agents.get("architect")
        
        self.prompt_needed.set()

        try:
            while not self.stop_event.is_set():
                self.process_plan_queue()
                
                if self.prompt_needed.is_set():
                    print("\nVocê> ", end="", flush=True)
                    self.prompt_needed.clear()

                try:
                    user_input = self.user_input_queue.get_nowait()
                    
                    if not user_input.strip():
                        self.prompt_needed.set()
                        continue
                    
                    if user_input.lower() in ["exit", "quit"]:
                        print("Encerrando..."); self.stop_event.set(); break
                    
                    self.project_in_progress.set()
                    self._cleanup_workspace()

                    print(f"\n[USER] Solicitação recebida. Acionando o Arquiteto...")
                    architect.create_master_plan(user_input)
                    
                except queue.Empty:
                    pass
                
                time.sleep(0.5)
                
        except KeyboardInterrupt:
            print("\nEncerrando..."); self.stop_event.set()
        
        logger.info("Aguardando threads de segundo plano finalizem...")
        for thread in self.background_threads: thread.join(timeout=2)
        print("Sistema encerrado.")

    def _cleanup_workspace(self):
        """Limpa arquivos temporários de planejamento de execuções anteriores."""
        logger.info("Limpando artefatos de planejamento do workspace...")
        plans_queue_dir = "workspace/plans_queue"
        if os.path.exists(plans_queue_dir):
            for f in os.listdir(plans_queue_dir):
                try:
                    os.remove(os.path.join(plans_queue_dir, f))
                except OSError as e:
                    logger.error(f"Erro ao limpar a fila de planos: {e}")