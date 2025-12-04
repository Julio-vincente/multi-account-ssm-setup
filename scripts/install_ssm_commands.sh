#!/bin/bash

echo "=== Comandos para instalar SSM Agent ==="
echo ""
echo "Execute estes comandos via SSH nas instâncias que não aparecem no SSM"
echo "A instalação NÃO reinicia a máquina e NÃO para serviços rodando"
echo ""

echo "### Amazon Linux 2 / Amazon Linux 2023:"
echo "sudo yum install -y amazon-ssm-agent"
echo "sudo systemctl enable amazon-ssm-agent"
echo "sudo systemctl start amazon-ssm-agent"
echo ""

echo "### Ubuntu / Debian:"
echo "sudo snap install amazon-ssm-agent --classic"
echo "sudo snap start amazon-ssm-agent"
echo ""

echo "### CentOS / RHEL:"
echo "sudo yum install -y https://s3.amazonaws.com/ec2-downloads-windows/SSMAgent/latest/linux_amd64/amazon-ssm-agent.rpm"
echo "sudo systemctl enable amazon-ssm-agent"
echo "sudo systemctl start amazon-ssm-agent"
echo ""

echo "### Windows (PowerShell como Admin):"
echo 'Invoke-WebRequest https://s3.amazonaws.com/ec2-downloads-windows/SSMAgent/latest/windows_amd64/AmazonSSMAgentSetup.exe -OutFile $env:USERPROFILE\Desktop\SSMAgent_latest.exe'
echo 'Start-Process -FilePath $env:USERPROFILE\Desktop\SSMAgent_latest.exe -ArgumentList "/S"'
echo ""

echo "### Verificar se instalou:"
echo "# Linux:"
echo "sudo systemctl status amazon-ssm-agent"
echo ""
echo "# Windows:"
echo "Get-Service AmazonSSMAgent"
echo ""

echo "Após instalar, aguarde 5-10 minutos e execute check_ssm_agent.py para verificar"
