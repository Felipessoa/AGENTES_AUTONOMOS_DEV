# src/core/orchestrator.py

# Adicione esta importação junto com as outras importações de agentes
from src.agents.git_agent import GitAgent

# NOTA: O código abaixo assume a estrutura existente da sua classe Orchestrator.
# Adapte conforme necessário, garantindo que as novas linhas sejam adicionadas
# nos locais corretos (__init__ e interactive_shell).

class Orchestrator:
    def __init__(self):
        """
        Inicializa o Orchestrator e todos os agentes disponíveis.
        """
        self.agents = {
            # ... outros agentes existentes podem estar aqui ...
            "git": GitAgent(),  # NOVO: Instancia o GitAgent
        }
        # ... resto do seu código __init__ ...

    def execute_task(self, task_description: str):
        """
        Um método de exemplo para executar uma tarefa.
        (Este método pode ou não existir no seu arquivo, é apenas um exemplo de estrutura)
        """
        print(f"Executando tarefa: {task_description}")
        # Lógica para delegar a tarefa a um agente...

    def interactive_shell(self):
        """
        Inicia um shell interativo para receber comandos do usuário.
        """
        print("Bem-vindo ao shell interativo. Digite 'exit' para sair.")
        print("Comandos disponíveis: commit \"<mensagem>\", exit")
        
        while True:
            try:
                user_input = input("Orchestrator> ")
                if not user_input.strip():
                    continue

                parts = user_input.split()
                command = parts[0].lower()
                # Junta todos os argumentos em uma única string
                args_str = " ".join(parts[1:])

                if command == "exit":
                    print("Saindo do shell.")
                    break

                # NOVO: Lógica para o comando 'commit'
                elif command == "commit":
                    if not args_str:
                        print("Erro: O comando 'commit' requer uma mensagem.")
                        print("Exemplo: commit \"Adiciona nova funcionalidade X\"")
                    else:
                        # Remove aspas do início e do fim, se existirem
                        commit_message = args_str.strip('"')
                        
                        print(f"Iniciando processo de commit com a mensagem: '{commit_message}'")
                        git_agent = self.agents["git"]
                        success = git_agent.run(commit_message=commit_message)
                        if success:
                            print("Processo de commit finalizado com sucesso.")
                        else:
                            print("Processo de commit falhou. Verifique os logs acima.")
                
                # ... outras lógicas de comando existentes podem estar aqui ...

                else:
                    print(f"Comando desconhecido: '{command}'")

            except KeyboardInterrupt:
                print("\nSaindo do shell.")
                break
            except Exception as e:
                print(f"Ocorreu um erro inesperado: {e}")
