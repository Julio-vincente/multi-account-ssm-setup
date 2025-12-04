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

def get_instance_name(tags):
    if not tags:
        return "N/A"
    for tag in tags:
        if tag['Key'] == 'Name':
            return tag['Value']
    return "N/A"

def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    output_file = os.path.join(script_dir, "../data/missing-from-ssm.csv")
    
    with open(output_file, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['Profile', 'Region', 'InstanceId', 'Name', 'HasRole'])
        
        print("=== Instâncias RUNNING que NÃO aparecem no SSM ===\n")
        
        total_running = 0
        total_in_ssm = 0
        total_missing = 0
        
        for profile in PROFILES:
            for region in REGIONS:
                try:
                    session = boto3.Session(profile_name=profile, region_name=region)
                    ec2 = session.client('ec2')
                    ssm = session.client('ssm')
                    
                    ec2_response = ec2.describe_instances(
                        Filters=[{'Name': 'instance-state-name', 'Values': ['running']}]
                    )
                    
                    running_instances = {}
                    for reservation in ec2_response['Reservations']:
                        for instance in reservation['Instances']:
                            instance_id = instance['InstanceId']
                            name = get_instance_name(instance.get('Tags'))
                            has_role = 'Yes' if instance.get('IamInstanceProfile') else 'No'
                            running_instances[instance_id] = {'name': name, 'has_role': has_role}
                            total_running += 1
                    
                    ssm_response = ssm.describe_instance_information()
                    ssm_instances = {i['InstanceId'] for i in ssm_response['InstanceInformationList']}
                    total_in_ssm += len(ssm_instances)
                    
                    missing = set(running_instances.keys()) - ssm_instances
                    
                    if missing:
                        print(f"{profile} - {region}:")
                        for instance_id in missing:
                            info = running_instances[instance_id]
                            writer.writerow([profile, region, instance_id, info['name'], info['has_role']])
                            print(f"  ❌ {instance_id} ({info['name']}) - Role: {info['has_role']}")
                            total_missing += 1
                        print()
                        
                except Exception as e:
                    pass
        
        print(f"=== Resumo ===")
        print(f"Total running: {total_running}")
        print(f"No SSM: {total_in_ssm}")
        print(f"Faltando: {total_missing}")
        print(f"\nArquivo salvo: {output_file}")

if __name__ == "__main__":
    main()
