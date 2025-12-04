#!/usr/bin/env python3

import boto3
import csv
import os
import sys

try:
    from config import PROFILES, REGIONS
except ImportError:
    print("❌ Arquivo config.py não encontrado!")
    print("Execute: cp ../config.example.py config.py")
    sys.exit(1)

def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    output_file = os.path.join(script_dir, "../data/ssm-agent-status.csv")
    
    with open(output_file, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['Profile', 'Region', 'InstanceId', 'PingStatus', 'AgentVersion', 'PlatformType'])
        
        print("=== Verificando instâncias no SSM ===\n")
        
        for profile in PROFILES:
            for region in REGIONS:
                print(f"Verificando: {profile} - {region}")
                
                try:
                    session = boto3.Session(profile_name=profile, region_name=region)
                    ssm = session.client('ssm')
                    
                    response = ssm.describe_instance_information()
                    
                    if not response['InstanceInformationList']:
                        print(f"  ℹ️  Nenhuma instância no SSM")
                    else:
                        for instance in response['InstanceInformationList']:
                            instance_id = instance['InstanceId']
                            ping_status = instance['PingStatus']
                            agent_version = instance.get('AgentVersion', 'N/A')
                            platform = instance.get('PlatformType', 'N/A')
                            
                            writer.writerow([profile, region, instance_id, ping_status, agent_version, platform])
                            
                            if ping_status == 'Online':
                                print(f"  ✅ {instance_id} - Online - {platform} - Agent: {agent_version}")
                            else:
                                print(f"  ⚠️  {instance_id} - {ping_status}")
                        
                except Exception as e:
                    print(f"  ⚠️  Erro: {str(e)}")
                
                print()
        
        print(f"=== Resultado salvo em: {output_file} ===")

if __name__ == "__main__":
    main()
