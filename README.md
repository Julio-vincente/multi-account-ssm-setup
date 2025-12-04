# SSM Implementation - AWS Multi-Account

Projeto para implementação e gerenciamento do AWS Systems Manager (SSM) em instâncias EC2 de múltiplas contas AWS.

## 📁 Estrutura

```
Roadcard/
├── scripts/                    # Scripts Python e Shell
│   ├── check_ssm_status.py    # Verifica status SSM das EC2s
│   ├── enable_ssm.py           # Habilita SSM nas instâncias
│   ├── check_ssm_agent.py     # Verifica instâncias no SSM
│   ├── compare_ec2_ssm.py     # Compara EC2 vs SSM
│   ├── install_ssm_via_runcommand.py  # Instala via Run Command
│   └── install_ssm_commands.sh # Comandos manuais de instalação
├── data/                       # Arquivos CSV e logs (gitignored)
│   ├── ec2-inventory.csv      # Inventário completo
│   ├── ssm-agent-status.csv   # Status dos agentes
│   ├── missing-from-ssm.csv   # Instâncias faltando
│   └── enable_ssm_output.log  # Log de execução
├── reports/                    # Relatórios e documentação
│   └── RELATORIO_SSM.md       # Relatório detalhado
├── config.example.py           # Exemplo de configuração
└── README.md                   # Este arquivo
```

## 🚀 Como Usar

### Configuração Inicial

1. Copie o arquivo de exemplo:
```bash
cp config.example.py scripts/config.py
```

2. Edite `scripts/config.py` com suas contas e regiões AWS

3. Configure AWS SSO:
```bash
aws sso login --profile YOUR_PROFILE
```

### 1. Verificar status SSM de todas as EC2s
```bash
cd scripts
python3 check_ssm_status.py
```
**Saída:** `data/ec2-inventory.csv`

### 2. Habilitar SSM nas instâncias sem configuração
```bash
cd scripts
python3 enable_ssm.py
```
**Ações:**
- Cria IAM Role + Instance Profile para instâncias sem role
- Adiciona policy SSM em roles existentes
- **NÃO reinicia instâncias**

### 3. Verificar quais instâncias aparecem no SSM
```bash
cd scripts
python3 check_ssm_agent.py
```
**Saída:** `data/ssm-agent-status.csv`

### 4. Comparar EC2 running vs SSM
```bash
cd scripts
python3 compare_ec2_ssm.py
```
**Saída:** `data/missing-from-ssm.csv`

### 5. Comandos para instalar agente SSM manualmente
```bash
cd scripts
bash install_ssm_commands.sh
```

## 📊 O que o projeto faz

- Verifica status SSM em múltiplas contas e regiões AWS
- Identifica instâncias sem IAM Role para SSM
- Cria automaticamente roles e instance profiles necessários
- Adiciona policies SSM em roles existentes
- Compara instâncias EC2 vs instâncias visíveis no SSM
- Gera relatórios em CSV para análise

## ⚙️ Pré-requisitos

- Python 3.x
- boto3 (`sudo apt install python3-boto3`)
- AWS CLI configurado com SSO
- Permissões IAM necessárias:
  - `ec2:DescribeInstances`
  - `iam:CreateRole`, `iam:AttachRolePolicy`
  - `iam:CreateInstanceProfile`, `iam:AddRoleToInstanceProfile`
  - `ssm:DescribeInstanceInformation`

## ⚠️ Importante

- **Nenhuma operação reinicia instâncias**
- Todas as mudanças são aplicadas em tempo real
- Instâncias podem levar 5-10 minutos para aparecer no SSM após configuração
- O agente SSM precisa estar instalado nas instâncias
- **Dados sensíveis estão no .gitignore** - não commite arquivos da pasta `data/`

## 📝 Políticas SSM Reconhecidas

O script reconhece as seguintes policies como válidas:
- `AmazonSSMManagedInstanceCore` (recomendada)
- `AmazonEC2RoleforSSM` (antiga, mas funcional)
- `AmazonSSMFullAccess` (completa)

## 🔒 Segurança

- Todos os arquivos com dados sensíveis estão no `.gitignore`
- Nunca commite arquivos CSV, logs ou configurações com IDs de contas
- Use `config.example.py` como template, não commite `config.py`

## 🆘 Suporte

Para dúvidas ou problemas, consulte o relatório em `reports/RELATORIO_SSM.md`
