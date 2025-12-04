#!/usr/bin/env python3
"""
Script para habilitar AWS Systems Manager (SSM) em instâncias EC2.

Este script lê o inventário gerado pelo check_ssm_status.py e habilita o SSM
nas instâncias que não possuem a configuração necessária.

Funcionalidades:
- Cria IAM Role com permissões SSM para instâncias sem role
- Adiciona policy SSM em roles existentes que não têm
- Associa Instance Profile às instâncias EC2

Uso:
    python3 enable_ssm.py

Pré-requisitos:
    - Arquivo ec2-inventory.csv gerado pelo check_ssm_status.py
    - Sessão SSO ativa (aws sso login)
    - Permissões IAM para criar roles e associar instance profiles
"""

import boto3
import csv
import sys

def create_ssm_role(iam_client, role_name):
    """
    Cria uma IAM Role com permissões para SSM.
    
    Args:
        iam_client: Cliente boto3 do IAM
        role_name: Nome da role a ser criada
    
    A role criada permite que o serviço EC2 assuma a role (trust policy)
    e anexa a policy AmazonSSMManagedInstanceCore que dá permissões para:
    - Registrar a instância no Systems Manager
    - Executar comandos remotos
    - Gerenciar patches e configurações
    """
    trust_policy = {
        "Version": "2012-10-17",
        "Statement": [{
            "Effect": "Allow",
            "Principal": {"Service": "ec2.amazonaws.com"},
            "Action": "sts:AssumeRole"
        }]
    }
    
    try:
        iam_client.create_role(
            RoleName=role_name,
            AssumeRolePolicyDocument=str(trust_policy).replace("'", '"'),
            Description="SSM role for EC2 instances"
        )
        print(f"    ✅ Role criada: {role_name}")
    except iam_client.exceptions.EntityAlreadyExistsException:
        print(f"    ℹ️  Role já existe: {role_name}")
    
    # Anexa a policy gerenciada da AWS para SSM
    iam_client.attach_role_policy(
        RoleName=role_name,
        PolicyArn="arn:aws:iam::aws:policy/AmazonSSMManagedInstanceCore"
    )
    print(f"    ✅ Policy SSM anexada à role")

def create_instance_profile(iam_client, profile_name, role_name):
    """
    Cria um Instance Profile e associa a role IAM.
    
    Args:
        iam_client: Cliente boto3 do IAM
        profile_name: Nome do instance profile a ser criado
        role_name: Nome da role a ser associada ao profile
    
    Instance Profile é o container que permite que uma EC2 use uma IAM Role.
    É necessário criar o profile e depois adicionar a role nele.
    """
    try:
        iam_client.create_instance_profile(InstanceProfileName=profile_name)
        print(f"    ✅ Instance Profile criado: {profile_name}")
    except iam_client.exceptions.EntityAlreadyExistsException:
        print(f"    ℹ️  Instance Profile já existe: {profile_name}")
    
    try:
        iam_client.add_role_to_instance_profile(
            InstanceProfileName=profile_name,
            RoleName=role_name
        )
        print(f"    ✅ Role adicionada ao Instance Profile")
    except:
        pass  # Role já está no profile

def attach_role_to_instance(ec2_client, iam_client, instance_id, profile_name):
    """
    Associa um Instance Profile a uma instância EC2.
    
    Args:
        ec2_client: Cliente boto3 do EC2
        iam_client: Cliente boto3 do IAM
        instance_id: ID da instância EC2
        profile_name: Nome do instance profile a ser associado
    
    Returns:
        bool: True se sucesso, False se erro
    
    Esta operação NÃO requer restart da instância. A associação é feita
    em tempo real e a instância começará a aparecer no SSM em alguns minutos.
    """
    try:
        ec2_client.associate_iam_instance_profile(
            IamInstanceProfile={'Name': profile_name},
            InstanceId=instance_id
        )
        print(f"    ✅ Instance Profile associado à EC2")
        return True
    except Exception as e:
        print(f"    ❌ Erro ao associar: {str(e)}")
        return False

def add_ssm_to_existing_role(iam_client, role_name):
    """
    Adiciona a policy SSM a uma role IAM existente.
    
    Args:
        iam_client: Cliente boto3 do IAM
        role_name: Nome da role existente
    
    Returns:
        bool: True se sucesso, False se erro
    
    Usado quando a instância já tem uma role, mas essa role não possui
    as permissões necessárias para SSM. Apenas adiciona a policy sem
    modificar nada mais na role.
    """
    try:
        iam_client.attach_role_policy(
            RoleName=role_name,
            PolicyArn="arn:aws:iam::aws:policy/AmazonSSMManagedInstanceCore"
        )
        print(f"    ✅ Policy SSM adicionada à role existente: {role_name}")
        return True
    except Exception as e:
        print(f"    ❌ Erro ao adicionar policy: {str(e)}")
        return False

def main():
    """
    Função principal que processa o inventário e habilita SSM.
    
    Fluxo:
    1. Lê o arquivo ec2-inventory.csv
    2. Filtra instâncias sem SSM (SSM_Status = NO_SSM)
    3. Para cada instância:
       - Se não tem role: cria role + instance profile + associa
       - Se tem role sem SSM: adiciona policy SSM na role existente
    4. Aguarda propagação das mudanças (10 segundos)
    
    O script é seguro e não modifica nada além do necessário para SSM.
    """
    inventory_file = "/home/julio/OpsTeam/Roadcard/ec2-inventory.csv"
    
    # Lê o inventário gerado anteriormente
    try:
        with open(inventory_file, 'r') as f:
            reader = csv.DictReader(f)
            instances = list(reader)
    except FileNotFoundError:
        print(f"❌ Arquivo {inventory_file} não encontrado. Execute check_ssm_status.py primeiro.")
        sys.exit(1)
    
    # Filtra apenas instâncias que precisam de correção
    instances_to_fix = [i for i in instances if i['SSM_Status'] == 'NO_SSM']
    
    if not instances_to_fix:
        print("✅ Todas as instâncias já têm SSM habilitado!")
        sys.exit(0)
    
    print(f"=== Encontradas {len(instances_to_fix)} instâncias sem SSM ===\n")
    
    # Processa cada instância
    for inst in instances_to_fix:
        print(f"Processando: {inst['InstanceId']} ({inst['Name']}) - {inst['Profile']} - {inst['Region']}")
        
        # Pula instâncias que não estão rodando
        if inst['State'] != 'running':
            print(f"  ⚠️  Instância não está running, pulando...")
            continue
        
        # Cria sessão AWS com o profile correto
        session = boto3.Session(profile_name=inst['Profile'], region_name=inst['Region'])
        ec2 = session.client('ec2')
        iam = session.client('iam')
        
        # Caso 1: Instância sem role - cria tudo do zero
        if inst['IAM_Role'] == 'NO_ROLE':
            role_name = f"SSM-Role-{inst['InstanceId']}"
            profile_name = f"SSM-Profile-{inst['InstanceId']}"
            
            print(f"  📝 Criando nova role e instance profile...")
            create_ssm_role(iam, role_name)
            create_instance_profile(iam, profile_name, role_name)
            
            # Aguarda propagação da role no IAM (necessário)
            import time
            print(f"  ⏳ Aguardando propagação da role...")
            time.sleep(10)
            
            attach_role_to_instance(ec2, iam, inst['InstanceId'], profile_name)
        
        # Caso 2: Instância com role mas sem policy SSM - adiciona policy
        else:
            print(f"  📝 Adicionando policy SSM à role existente: {inst['IAM_Role']}")
            add_ssm_to_existing_role(iam, inst['IAM_Role'])
        
        print()
    
    print("=== Processo concluído! ===")
    print("Execute check_ssm_status.py novamente para verificar o resultado.")
    print("\nObs: As instâncias podem levar alguns minutos para aparecer no SSM.")

if __name__ == "__main__":
    main()
