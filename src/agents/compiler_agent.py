# src/agents/compiler_agent.py

import os
import subprocess
from src.core.functional_agent import FunctionalAgent # <-- CORREÇÃO DA IMPORTAÇÃO
from src.core.logger import get_logger
# Precisamos importar o ExecutionAgent para usá-lo
from src.agents.execution_agent import ExecutionAgent 

class CompilerAgent(FunctionalAgent):
    """
    Agente funcional que empacota scripts Python em executáveis usando PyInstaller.
    """
    def __init__(self):
        super().__init__(agent_name="Compiler")
        self.logger = get_logger(self.agent_name)
        # Este agente precisa do ExecutionAgent para rodar comandos de forma segura
        # No entanto, não podemos instanciá-lo aqui ou teremos dependências circulares
        # Vamos pegar o executor do Orquestrador quando for a hora.
        # Por enquanto, vamos simplificar e usar o ExecutionAgent diretamente.
        # NOTA: Uma arquitetura melhor seria passar o executor como dependência.
        # Vamos criar uma instância simples por enquanto.
        self.executor = ExecutionAgent() 
        self._check_pyinstaller()

    def _check_pyinstaller(self):
        """Verifica se o PyInstaller está instalado e, se não, instala."""
        self.logger.debug("Verificando instalação do PyInstaller...")
        try:
            subprocess.run(["pip", "show", "pyinstaller"], check=True, capture_output=True)
            self.logger.debug("PyInstaller já está instalado.")
        except subprocess.CalledProcessError:
            self.logger.info("PyInstaller não encontrado. Instalando...")
            print("[USER] Dependência necessária (pyinstaller) não encontrada. Instalando...")
            self.executor.run("pip install pyinstaller")

    def run(self, script_path: str):
        """
        Executa o PyInstaller para compilar o script fornecido.

        Args:
            script_path: O caminho para o script Python principal (ex: workspace/hello.py)
        """
        if not os.path.exists(script_path):
            print(f"[USER] ❌ Erro de Compilação: Arquivo não encontrado em '{script_path}'")
            self.logger.error(f"Arquivo para compilação não encontrado: {script_path}")
            return

        script_name = os.path.splitext(os.path.basename(script_path))[0]
        output_name = f"{script_name}_app" # Nome final do executável

        # Comando de compilação
        command = (
            f"pyinstaller --onefile --noconsole "
            f"--name \"{output_name}\" "
            f"--distpath \"workspace/dist\" " # Coloca o executável final em workspace/dist
            f"--workpath \"workspace/build\" " # Coloca arquivos temporários em workspace/build
            f"\"{script_path}\""
        )

        print(f"[USER] Compilando '{script_path}'... Isso pode levar alguns minutos.")
        self.logger.info(f"Executando comando de compilação: {command}")
        
        # Delega a execução ao ExecutionAgent para manter a segurança
        self.executor.run(command)
        
        final_path = f"workspace/dist/{output_name}"
        if os.path.exists(final_path):
            print(f"[USER] ✅ Compilação concluída! Executável disponível em: {final_path}")
        else:
            print("[USER] ❌ Compilação falhou. Verifique os logs.")