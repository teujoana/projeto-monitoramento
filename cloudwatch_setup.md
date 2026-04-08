# 🛠️ Guia de Configuração: CloudWatch + SNS + Lambda

Siga estes passos para configurar o monitoramento automático na sua conta AWS:

### 1. Criar um Tópico SNS (Simple Notification Service)
- No console da AWS, vá para **SNS** > **Topics** > **Create topic**.
- Escolha o tipo **Standard** e dê um nome (ex: `Alerta-CPU-EC2`).
- Clique em **Create topic** e anote o **ARN** gerado — você vai precisar dele nos próximos passos.

### 2. Criar a Função Lambda
- Vá para **Lambda** > **Create function**.
- Escolha **Author from scratch**.
- Nome: `Notificador-Discord-Alarme`.
- Runtime: **Python 3.12** (versão atual recomendada; evite 3.11 que entra em fim de suporte em 2025).
- Clique em **Create function**.
- No editor de código, cole o conteúdo do arquivo `lambda_function.py`.
- **Obrigatório**: Vá na aba **Configuration** > **Environment variables** > **Edit** e adicione:
  - Chave: `WEBHOOK_URL`
  - Valor: URL completa do seu Webhook do Discord ou Slack.
  - ⚠️ **Nunca coloque o Webhook diretamente no código-fonte.**

### 3. Ajustar as Permissões IAM da Lambda (importante!)
- Ainda na página da função Lambda, vá em **Configuration** > **Permissions**.
- Clique no nome da **Execution role** para abrir o IAM.
- Adicione a policy `AWSLambdaBasicExecutionRole` se ainda não estiver presente (permite gravar logs no CloudWatch Logs).
- Para que a Lambda possa descrever instâncias EC2 (opcional, mas útil), adicione também a permissão `ec2:DescribeInstances` em uma policy inline.

### 4. Conectar a Lambda ao SNS
- Na página da função Lambda, clique em **Add trigger**.
- Selecione **SNS** e escolha o tópico criado no Passo 1.
- Clique em **Add**.

### 5. Criar o Alarme no CloudWatch
- Vá para **CloudWatch** > **Alarms** > **All alarms** > **Create alarm**.
- Clique em **Select metric** > **EC2** > **Per-Instance Metrics**.
- Escolha a métrica `CPUUtilization` da sua instância EC2.
- Configure o limite (ex: `Greater than 80%` por 2 períodos consecutivos de 5 minutos — evita falsos positivos de picos curtos).
- Na seção **Notification**, selecione o tópico SNS criado no Passo 1 para os estados **In alarm** e **OK**.
- Finalize a criação do alarme.

### 6. Testar a Automação
Você pode simular um evento SNS diretamente no console da Lambda para validar sem precisar estressar a EC2:
- Na página da função, clique em **Test** > **Create new test event**.
- Use o template **SNS** disponível na lista e clique em **Test**.

Para testar com carga real na instância EC2 (Amazon Linux 2023):
```bash
sudo dnf install stress -y
stress --cpu 1 --timeout 300
```
> ⚠️ No Amazon Linux 2023, use `dnf` em vez de `amazon-linux-extras` — o comando antigo não existe nessa versão.

Em poucos minutos você receberá a notificação no Discord/Slack! 🚀
