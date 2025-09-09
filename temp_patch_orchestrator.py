import os

def FILE_PATH = 'src/core/orchestrator.py'

def apply_patch():
    if not os.path.exists(FILE_PATH):
        print(f"Error: File not found at {FILE_PATH}")
        return

    with open(FILE_PATH, 'r') as f:
        lines = f.readlines()

    # --- Step 2: Add import ---
    import_to_add = 'from src.agents.execution_agent import ExecutionAgent\n'
    import_exists = any(import_to_add.strip() in line for line in lines)
    if not import_exists:
        class_def_index = -1
        for i, line in enumerate(lines):
            if line.strip().startswith('class Orchestrator'):
                class_def_index = i
                break
        if class_def_index != -1:
            lines.insert(class_def_index, import_to_add + '\n')
        else:
            # Fallback if class is not found, add after last import
            last_import_index = -1
            for i, line in enumerate(lines):
                if line.strip().startswith('import ') or line.strip().startswith('from '):
                    last_import_index = i
            lines.insert(last_import_index + 1, import_to_add)

    # --- Step 3: Add ExecutionAgent ---
    agent_added = any('"executor":' in line for line in lines)
    if not agent_added:
        for i, line in enumerate(lines):
            if '"code_generator": CodeGeneratorAgent(self.state)' in line:
                # Add comma to current line if it doesn't have one
                if not line.strip().endswith(','):
                    lines[i] = line.rstrip().replace('\n', '') + ',\n'
                # Insert new line after
                lines.insert(i + 1, '        "executor": ExecutionAgent(),\n')
                break

    # --- Step 4: Add 'run' block ---
    run_block_exists = any('elif command == "run":' in line for line in lines)
    if not run_block_exists:
        commit_block_start_index = -1
        commit_block_indent = -1
        for i, line in enumerate(lines):
            if 'if command == "commit":' in line.strip():
                commit_block_start_index = i
                commit_block_indent = len(line) - len(line.lstrip())
                break
        
        if commit_block_start_index != -1:
            commit_block_end_index = -1
            for i in range(commit_block_start_index + 1, len(lines)):
                line = lines[i]
                if line.strip(): # if not a blank line
                    current_indent = len(line) - len(line.lstrip())
                    if current_indent <= commit_block_indent:
                        commit_block_end_index = i
                        break
            
            if commit_block_end_index == -1: # Block goes to end of file
                commit_block_end_index = len(lines)

            run_block_lines = [
                'elif command == "run":\n',
                '    if not args:\n',
                '        print("Erro: O comando \'run\' requer um argumento.")\n',
                '        print("Uso: run <comando_a_ser_executado>")\n',
                '        continue\n',
                '    \n',
                '    # Converte a lista de argumentos de volta para uma string de comando\n',
                '    command_to_run = " ".join(args)\n',
                '    print(f"Executando comando: \'{command_to_run}\'...")\n',
                '    self.agents["executor"].run(command_to_run)\n'
            ]
            
            # Apply correct indentation
            indented_run_block = [(' ' * commit_block_indent) + line for line in run_block_lines]

            lines[commit_block_end_index:commit_block_end_index] = indented_run_block

    # --- Step 5: Overwrite the file ---
    with open(FILE_PATH, 'w') as f:
        f.writelines(lines)

    print(f"File '{FILE_PATH}' patched successfully.")

if __name__ == "__main__":
    apply_patch()
