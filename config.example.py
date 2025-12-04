"""
Arquivo de exemplo de configuração.
Copie para scripts/config.py e ajuste com suas contas e regiões.

cp config.example.py scripts/config.py
"""

# Lista de profiles AWS configurados no seu SSO
PROFILES = [
    "account1-env1",
    "account1-env2",
    "account2-env1",
    "account2-env2",
    # Adicione seus profiles aqui
]

# Regiões AWS a serem verificadas
REGIONS = [
    "us-east-1",
    "sa-east-1"
]

# Políticas SSM reconhecidas como válidas
SSM_POLICIES = [
    'AmazonSSMManagedInstanceCore',
    'AmazonEC2RoleforSSM',
    'AmazonSSMFullAccess'
]
