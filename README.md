# 🚨 AWS CloudWatch Monitoring & Automation (Serverless)

Este projeto demonstra a implementação de um sistema de **Monitoramento e Observabilidade** automatizado na **AWS**. Utilizando **CloudWatch**, **SNS** e **AWS Lambda**, o sistema detecta anomalias em instâncias EC2 (como alto uso de CPU) e envia notificações em tempo real para ferramentas de comunicação como **Discord** ou **Slack**.

## 🏗️ Arquitetura do Projeto

A solução foi construída utilizando uma arquitetura **Serverless** e orientada a eventos:
- **AWS CloudWatch**: Monitora métricas de performance (CPU, Memória, Disco) e dispara alarmes baseados em limites pré-definidos.
- **AWS SNS (Simple Notification Service)**: Atua como o barramento de mensagens que recebe o alerta do CloudWatch.
- **AWS Lambda (Python)**: Função serverless que processa a mensagem do SNS, formata os dados e realiza uma requisição HTTP (Webhook) para o destino final.
- **Discord/Slack**: Recebe a notificação formatada com detalhes do alarme (Nome, Estado, Motivo e Instância).

## 🛠️ Tecnologias Utilizadas

- **Cloud Provider**: AWS (CloudWatch, SNS, Lambda, EC2)
- **Linguagem**: Python 3.11+
- **Integração**: Webhooks (Discord/Slack)
- **Segurança**: Variáveis de Ambiente (Environment Variables) para gestão de segredos.

## 📂 Estrutura de Arquivos

- `lambda_function.py`: Código-fonte da função Lambda responsável pelo processamento e envio das notificações. Inclui validações de entrada, extração dinâmica do ID da instância EC2, tratamento de erros granular e logging estruturado via `logging` (CloudWatch Logs).
- `cloudwatch_setup.md`: Guia detalhado de configuração dos serviços no console da AWS, incluindo ajuste de permissões IAM e instrução de teste sem carga real.

## 🚀 Benefícios da Solução

- **Redução do MTTR (Mean Time To Repair)**: Notificações instantâneas permitem que a equipe de suporte aja rapidamente antes que o problema afete o usuário final.
- **Custo Zero (Free Tier)**: Todos os serviços utilizados estão dentro da camada gratuita da AWS para pequenos volumes de monitoramento.
- **Escalabilidade**: A arquitetura serverless escala automaticamente conforme o número de alarmes e instâncias monitoradas aumenta.

---
**Desenvolvido por Joana Aghata Dias Cardoso**  
*Suporte Técnico N1 | Cloud AWS | Análise de Dados*
