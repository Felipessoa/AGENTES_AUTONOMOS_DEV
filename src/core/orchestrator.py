# src/core/orchestrator.py

import os
import shlex
import threading
import time

# Importando os agentes
from src.agents.architect_agent import ArchitectAgent
from src.agents.backend_agent import BackendAgent
from src.agents.auditor_agent import AuditorAgent
from src.agents.git_agent import GitAgent
from src.agents.execution_agent import ExecutionAgent

# Importando o nosso novo sistema de logging
from src.core.logger import get_logger

# Criando uma instância do logger específica para este módulo
logger = get_logger("Orchestrator")

class Orchestrator:
    """
    O cérebro do sistema. Gerencia o ciclo de vida dos agentes
    e orquestra a execução de tarefas de forma síncrona com feedback ao usuário.
    """
    def __init__(self):
        logger.info("Inicializando o Orquestrador...")
        self.agents = {
            "architect": ArchitectAgent(),
            "backend": BackendAgent(project_root="."),
            "auditor": AuditorAgent(),
            "git": GitAgent(),
            "executor": ExecutionAgent()
        }
        self.stop_event = threading.Event()
        self.background_threads = []
        
        logger.info(f"Agentes carregados: {list(self.agents.keys())}")
        print("Orquestrador pronto.") # Mensagem inicial para o usuário

    def execute_task(self, task_prompt: str):
        """
        Executa um ciclo de desenvolvimento síncrono com feedback claro para o usuário.
        """
        # Usamos print() para feedback direto ao usuário, e logger para logs internos.
        print("\n[USER] Tarefa recebida. Orquestrando agentes...")
        
        architect = self.agents.get("architect")
        backend_dev = self.agents.get("backend")

        # --- Etapa 1: Planejamento ---
        try:
            print("[USER] Passo 1/2: Arquiteto está planejando...")
            
            # Limpa o plano antigo para evitar confusão
            plan_path = 'workspace/plan.md'
            if os.path.exists(plan_path):
                os.remove(plan_path)

            prompt_for_architect = f"Crie um plano de desenvolvimento detalhado para: '{task_prompt}'"
            development_plan = architect.think(prompt_for_architect)
            
            if not development_plan or development_plan.startswith("Erro:"):
                raise Exception("Arquiteto falhou em gerar um plano válido.")
            
            architect.write_to_workspace('plan.md', development_plan)
            logger.info("Plano de desenvolvimento criado com sucesso.")

        except Exception as e:
            print(f"[USER] ❌ Erro na etapa de planejamento: {e}")
            logger.error(f"Falha no planejamento: {e}", exc_info=True)
            return

        # --- Etapa 2: Construção ---
        try:
            print("[USER] Passo 2/2: Plano recebido. Backend está construindo...")
            backend_dev.run() # O método run do backend já lê o plan.md
            logger.info("Backend concluiu a execução do plano.")

        except Exception as e:
            print(f"[USER] ❌ Erro na etapa de construção: {e}")
            logger.error(f"Falha na construção: {e}", exc_info=True)
            return
        
        # --- Conclusão ---
        print("[USER] ✅ Tarefa concluída com sucesso!")

    def start_background_agents(self):
        """
        Inicia os agentes que devem rodar continuamente em threads separadas (apenas o Auditor).
        """
        logger.info("Iniciando agentes de segundo plano...")
        
        auditor_agent = self.agents.get("auditor")
        if auditor_agent:
            thread = threading.Thread(target=auditor_agent.run, args=(self.stop_event,), daemon=True)
            thread.start()
            self.background_threads.append(thread)
            logger.info(f"Agente '{auditor_agent.agent_name}' está rodando em segundo plano.")

    def interactive_shell(self):
        """
        Inicia o shell interativo para receber comandos do usuário.
        """
        self.start_background_agents()

        print("\n--- Shell de Orquestração Ativado ---")
        print("Comandos disponíveis: build, commit, run, exit")
        
        try:
            while not self.stop_event.is_set():
                command_input = input("\nOrquestrador> ")
                
                if command_input.lower() in ["exit", "quit"]:
                    print("Encerrando o Orquestrador...")
                    self.stop_event.set()
                    break
                
                parts = shlex.split(command_input)
                if not parts:
                    continue

                command = parts[0].lower()
                args = " ".join(parts[1:])

                if command == "build":
                    if not args:
                        print("[USER] Erro: O comando 'build' requer uma descrição.")
                        continue
                    self.execute_task(args) # Chamada síncrona
                
                elif command == "commit":
                    if not args:
                        print("[USER] Erro: O comando 'commit' requer uma mensagem.")
                        continue
                    self.agents.get("git").run(commit_message=args)

                elif command == "run":
                    if not args:
                        print("[USER] Erro: O comando 'run' requer um comando a ser executado.")
                        continue
                    self.agents.get("executor").run(command_to_execute=args)

                else:
                    print(f"[USER] Comando desconhecido: '{command}'.")
                
        except KeyboardInterrupt:
            print("\nEncerrando o Orquestrador (Ctrl+C)...")
            self.stop_event.set()
        
        logger.info("Aguardando threads de segundo plano finalizarem...")
        for thread in self.background_threads:
            thread.join(timeout=2)
        print("Sistema encerrado.")