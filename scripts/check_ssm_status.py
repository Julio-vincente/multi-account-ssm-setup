#!/usr/bin/env python3

import boto3
import csv
import os
import sys

# Importar configuração
try:
    from config import PROFILES, REGIONS, SSM_POLICIES
except ImportError:
    print("❌ Arquivo config.py não encontrado!")
    print("Execute: cp ../config.example.py config.py")
    print("E edite config.py com suas contas AWS")
    sys.exit(1)

def get_instance_name(tags):
    if not tags:
        return "N/A"
    for tag in tags:
        if tag['Key'] == 'Name':
            return tag['Value']
    return "N/A"

def get_role_from_instance_profile(iam_client, instance_profile_arn):
    try:
        profile_name = instance_profile_arn.split('/')[-1]
        response = iam_client.get_instance_profile(InstanceProfileName=profile_name)
        roles = response['InstanceProfile'].get('Roles', [])
        if roles:
            return roles[0]['RoleName']
    except:
        pass
    return None

def check_ssm_policy(iam_client, role_name):
    try:
        response = iam_client.list_attached_role_policies(RoleName=role_name)
        for policy in response['AttachedPolicies']:
            if policy['PolicyName'] in SSM_POLICIES:
                return True
        return False
    except:
        return False

def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    output_file = os.path.join(script_dir, "../data/ec2-inventory.csv")
    
    with open(output_file, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['Profile', 'Region', 'InstanceId', 'Name', 'State', 'IAM_Role', 'SSM_Status'])
        
        print("=== Coletando inventário de EC2s ===\n")
        
        for profile in PROFILES:
            for region in REGIONS:
                print(f"Verificando: {profile} - {region}")
                
                try:
                    session = boto3.Session(profile_name=profile, region_name=region)
                    ec2 = session.client('ec2')
                    iam = session.client('iam')
                    
                    response = ec2.describe_instances()
                    
                    instance_count = 0
                    for reservation in response['Reservations']:
                        for instance in reservation['Instances']:
                            instance_count += 1
                            instance_id = instance['InstanceId']
                            name = get_instance_name(instance.get('Tags'))
                            state = instance['State']['Name']
                            
                            iam_profile = instance.get('IamInstanceProfile')
                            
                            if not iam_profile:
                                writer.writerow([profile, region, instance_id, name, state, 'NO_ROLE', 'NO_SSM'])
                                print(f"  ❌ {instance_id} ({name}) - SEM IAM Role")
                            else:
                                role_arn = iam_profile['Arn']
                                role_name = get_role_from_instance_profile(iam, role_arn)
                                
                                if not role_name:
                                    writer.writerow([profile, region, instance_id, name, state, 'ERROR_ROLE', 'NO_SSM'])
                                    print(f"  ❌ {instance_id} ({name}) - Erro ao obter role")
                                else:
                                    has_ssm = check_ssm_policy(iam, role_name)
                                    
                                    if has_ssm:
                                        writer.writerow([profile, region, instance_id, name, state, role_name, 'OK'])
                                        print(f"  ✅ {instance_id} ({name}) - SSM OK")
                                    else:
                                        writer.writerow([profile, region, instance_id, name, state, role_name, 'NO_SSM'])
                                        print(f"  ⚠️  {instance_id} ({name}) - Role sem SSM")
                    
                    if instance_count == 0:
                        print(f"  ℹ️  Nenhuma instância encontrada")
                        
                except Exception as e:
                    print(f"  ⚠️  Erro ao acessar: {str(e)}")
                
                print()
        
        print(f"=== Inventário salvo em: {output_file} ===")

if __name__ == "__main__":
    main()
