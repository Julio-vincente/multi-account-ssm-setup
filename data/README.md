# Data Directory

⚠️ **ATENÇÃO:** Este diretório contém dados sensíveis e está no .gitignore

## Arquivos gerados pelos scripts:

- `ec2-inventory.csv` - Inventário completo de instâncias EC2
- `ssm-agent-status.csv` - Status dos agentes SSM
- `missing-from-ssm.csv` - Instâncias que faltam no SSM
- `enable_ssm_output.log` - Log de execução do enable_ssm.py

## ⚠️ Nunca commite estes arquivos!

Eles contêm:
- IDs de instâncias
- Nomes de recursos
- Informações de contas AWS
- Nomes de roles IAM
