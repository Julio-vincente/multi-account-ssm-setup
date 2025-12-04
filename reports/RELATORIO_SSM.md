# Relatório de Implementação SSM - Multi-Account

Relatório de exemplo da implementação do AWS Systems Manager em múltiplas contas.

## 📊 Resumo Geral

- **Total de instâncias:** XXX
- **✅ Com SSM configurado:** XXX (XX%)
- **⚠️ Pendentes:** X (X%)

## ✅ Instâncias Configuradas com Sucesso

As instâncias agora têm SSM habilitado e funcionando:
- Instâncias com roles existentes: Policy SSM adicionada
- Instâncias sem role: Nova role + instance profile criados
- Instâncias com `AmazonEC2RoleforSSM`: Reconhecidas como OK

### Contas processadas:
- account1-env1
- account1-env2
- account2-env1
- (configure suas contas no config.py)

### Regiões:
- us-east-1 (Virginia)
- sa-east-1 (São Paulo)
- (configure suas regiões no config.py)

## ⚠️ Instâncias Pendentes

Instâncias que estão **STOPPED** (desligadas) ou com problemas:

| Instance ID | Nome | Conta | Região | Status | Motivo |
|-------------|------|-------|--------|--------|--------|
| i-xxxxxxxxx | example-instance | account-env | us-east-1 | stopped | Erro ao obter role |

**Ação recomendada:** Quando essas instâncias forem iniciadas, execute novamente o script `enable_ssm.py`.

## 🔧 Scripts Criados

1. **check_ssm_status.py** - Verifica status SSM de todas as EC2s
2. **enable_ssm.py** - Habilita SSM nas instâncias automaticamente
3. **check_ssm_agent.py** - Verifica instâncias visíveis no SSM
4. **compare_ec2_ssm.py** - Compara EC2 running vs SSM

## ✅ Políticas SSM Reconhecidas

O script reconhece as seguintes policies como válidas para SSM:
- `AmazonSSMManagedInstanceCore` (recomendada)
- `AmazonEC2RoleforSSM` (antiga, mas funcional)
- `AmazonSSMFullAccess` (completa)

## 🚀 Como Usar

### Verificar status atual:
```bash
cd scripts
python3 check_ssm_status.py
```

### Habilitar SSM nas pendentes:
```bash
cd scripts
python3 enable_ssm.py
```

### Ver inventário:
```bash
cat data/ec2-inventory.csv
```

## ⚠️ Importante

- **Nenhuma instância foi reiniciada** durante o processo
- Todas as mudanças foram aplicadas em tempo real
- As instâncias podem levar 5-10 minutos para aparecer no Systems Manager após a configuração
- O agente SSM precisa estar instalado nas instâncias

## 📝 Notas Técnicas

- Instâncias sem role: Criada nova role `SSM-Role-{instance-id}` com policy SSM
- Instâncias com role: Policy SSM adicionada à role existente
- Limite de policies: Algumas roles podem atingir o limite de 10 managed policies
