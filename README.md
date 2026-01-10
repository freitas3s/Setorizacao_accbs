# ACC-BS – Sistema de Setorização Operacional

Aplicação web desenvolvida em **Streamlit** para gestão e visualização operacional da setorização **ACC/APP**, com atualização em tempo real, foco em coordenação entre consoles e suporte a múltiplas regiões.

O sistema foi projetado para uso operacional, priorizando **estabilidade**, **clareza visual** e **controle de estado** rigoroso.

## Finalidade

O sistema permite operação em dois modos distintos:

### **Supervisão**
- Configurar a setorização de cada região
- Agrupar setores por console (CTR)
- Atualizar o estado operacional centralizado
- Gerenciar configurações em tempo real

### **Consoles Operacionais**
- Visualizar setores atualmente alocados ao console
- Identificar setores de fronteira automaticamente
- Ver em qual console e região estão os setores adjacentes
- Operar em modo travado (sem risco de alteração acidental)

## Conceitos de Funcionamento

### Modo Operacional
- **Cada navegador representa um console** específico
- **Região e console são definidos na entrada** do sistema
- **Após confirmação:**
  - O console fica travado em sua configuração
  - O estado não se altera com auto-refresh
  - Garante segurança e previsibilidade operacional

### Atualização em Tempo Real
- **Atualização automática** via `st_autorefresh`
- **Leitura direta do banco SQLite** sem intermediários
- **Consoles refletem alterações** feitas por supervisores em poucos segundos
- **Não depende de WebSockets** ou conexões complexas

## Estrutura do Projeto

├── app.py # App principal - ponto de entrada ├── consoles.py # Visualização operacional dos consoles ├── supervisores.py # Tela de supervisão (edição da setorização) ├── setorizacao.py # Dados fixos (regiões, setores e fronteiras) ├── setorizacao.db # Banco SQLite ├── requirements.txt # Dependências do projeto └── .streamlit/ └── config.toml # Tema dark padrão


## Regiões Suportadas

O sistema opera com **4 regiões** principais:

| Região | Descrição | Características |
|--------|-----------|-----------------|
| **RRJ** | Rio de Janeiro | Consoles específicos, conjunto próprio de setores |
| **RSP** | São Paulo | Regras independentes de fronteira |
| **RBR** | Brasília | Configuração personalizada |
| **FIS** | Fiscalização | Suporte especial para modo AGRUPADO |

**Cada região possui:**
- Consoles específicos
- Conjunto próprio de setores
- Regras independentes de fronteira

## Banco de Dados

**SQLite** – `setorizacao.db`

### Estrutura Principal

```sql
CREATE TABLE setorizacao (
    regiao TEXT,
    ctr TEXT,
    setor TEXT
);
