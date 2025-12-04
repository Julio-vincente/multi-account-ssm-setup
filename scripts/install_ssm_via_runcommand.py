#!/usr/bin/env python3
"""
Script para instalar SSM Agent usando Run Command nas instâncias que já têm SSM.
"""

import boto3
import csv
import os
import time

def install_ssm_agent(ssm_client, instance_id, platform):
    """Instala SSM Agent baseado na plataforma"""
    
    if platform == 'Linux':
        commands = [
            '#!/bin/bash',
            'if command -v yum &> /dev/null; then',
            '  sudo yum install -y amazon-ssm-agent',
            '  sudo systemctl enable amazon-ssm-agent',
            '  sudo systemctl start amazon-ssm-agent',
            'elif command -v snap &> /dev/null; then',
            '  sudo snap install amazon-ssm-agent --classic',
            '  sudo snap start amazon-ssm-agent',
            'fi'
        ]
    elif platform == 'Windows':
        commands = [
            '$url = "https://s3.amazonaws.com/ec2-downloads-windows/SSMAgent/latest/windows_amd64/AmazonSSMAgentSetup.exe"',
            '$output = "$env:TEMP\\SSMAgent_latest.exe"',
            'Invoke-WebRequest -Uri $url -OutFile $output',
            'Start-Process -FilePath $output -ArgumentList "/S" -Wait'
        ]
    else:
        return None
    
    try:
        response = ssm_client.send_command(
            InstanceIds=[instance_id],
            DocumentName='AWS-RunShellScript' if platform == 'Linux' else 'AWS-RunPowerShellScript',
            Parameters={'commands': commands},
            TimeoutSeconds=300
        )
        return response['Command']['CommandId']
    except Exception as e:
        print(f"    ❌ Erro: {str(e)}")
        return None

def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    ssm_status_file = os.path.join(script_dir, "../data/ssm-agent-status.csv")
    
    # Ler instâncias que já estão no SSM
    try:
        with open(ssm_status_file, 'r') as f:
            reader = csv.DictReader(f)
            ssm_instances = list(reader)
    except FileNotFoundError:
        print("❌ Execute check_ssm_agent.py primeiro!")
        return
    
    # Filtrar apenas instâncias Online
    online_instances = [i for i in ssm_instances if i['PingStatus'] == 'Online']
    
    if not online_instances:
        print("❌ Nenhuma instância online no SSM para usar como base")
        return
    
    print(f"=== Instalando SSM Agent via Run Command ===")
    print(f"Instâncias online disponíveis: {len(online_instances)}\n")
    
    # Verificar versão do agente (se muito antiga, atualizar)
    for inst in online_instances[:5]:  # Testar nas primeiras 5
        print(f"Testando: {inst['InstanceId']} ({inst['Profile']} - {inst['Region']})")
        print(f"  Platform: {inst['PlatformType']}")
        print(f"  Agent Version: {inst['AgentVersion']}")
        
        session = boto3.Session(profile_name=inst['Profile'], region_name=inst['Region'])
        ssm = session.client('ssm')
        
        # Verificar se agente está atualizado
        version = inst['AgentVersion']
        major_version = int(version.split('.')[0])
        
        if major_version < 3:
            print(f"  ⚠️  Agente desatualizado, atualizando...")
            command_id = install_ssm_agent(ssm, inst['InstanceId'], inst['PlatformType'])
            if command_id:
                print(f"  ✅ Comando enviado: {command_id}")
        else:
            print(f"  ✅ Agente já está atualizado")
        
        print()
    
    print("=== Processo concluído! ===")
    print("Aguarde 5-10 minutos e execute check_ssm_agent.py novamente")

if __name__ == "__main__":
    main()
