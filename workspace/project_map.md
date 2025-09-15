# Mapa do Projeto e Regras de Arquitetura

Este documento é a fonte da verdade sobre a estrutura do projeto. É mantido pelo LibrarianAgent.

### Diretório: `src/core` (✅ Encontrado)
- **Descrição/Regra:** Contém os componentes centrais e a lógica de arquitetura do sistema (Orchestrator, BaseAgent). Regra: Apenas código de infraestrutura crítica.

### Diretório: `src/agents` (✅ Encontrado)
- **Descrição/Regra:** Contém a implementação de cada agente individual. Regra: Cada novo agente deve ter seu próprio arquivo aqui.

### Diretório: `workspace` (✅ Encontrado)
- **Descrição/Regra:** Diretório de trabalho para operações. Contém subpastas para artefatos gerados.

### Diretório: `workspace/output` (✅ Encontrado)
- **Descrição/Regra:** Diretório padrão para a saída de projetos gerados. Regra: Todos os novos projetos devem ser criados aqui.

### Diretório: `logs` (✅ Encontrado)
- **Descrição/Regra:** Contém todos os logs do sistema.

### Ambiente
- **Descrição/Regra:** O sistema operacional é Linux (WSL). Use comandos de shell compatíveis (ex: `xdg-open`, `rm -r`). O comando `open` (macOS) não funcionará.

