import json
import os
import urllib3
import logging

# Configuração de logging (substitui print() para funcionar melhor no CloudWatch Logs)
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Webhook URL obrigatoriamente via variável de ambiente — nunca hardcoded
WEBHOOK_URL = os.environ.get('WEBHOOK_URL')

http = urllib3.PoolManager()


def get_instance_id(sns_message: dict) -> str:
    """
    Tenta extrair o ID da instância EC2 a partir das dimensões do alarme do CloudWatch.
    Retorna 'N/A' se não encontrado.
    """
    try:
        dimensions = sns_message.get('Trigger', {}).get('Dimensions', [])
        for dim in dimensions:
            if dim.get('name') == 'InstanceId':
                return dim.get('value', 'N/A')
    except Exception:
        pass
    return 'N/A'


def build_discord_payload(alarm_name: str, new_state: str, reason: str, instance_id: str) -> dict:
    """Monta o payload no formato de Embed do Discord."""
    color = 15158332 if new_state == 'ALARM' else 3066993  # Vermelho para ALARM, Verde para OK
    emoji = "🚨" if new_state == 'ALARM' else "✅"

    return {
        "content": f"{emoji} **Alerta de Monitoramento AWS**",
        "embeds": [{
            "title": f"Alarme: {alarm_name}",
            "description": f"O estado do alarme mudou para: **{new_state}**",
            "color": color,
            "fields": [
                {"name": "Motivo", "value": reason, "inline": False},
                {"name": "Instância", "value": instance_id, "inline": True}
            ],
            "footer": {"text": "Monitoramento Automático via AWS Lambda"}
        }]
    }


def send_webhook(payload: dict) -> int:
    """Envia o payload para o Webhook configurado. Retorna o status HTTP."""
    encoded_msg = json.dumps(payload).encode('utf-8')
    resp = http.request(
        'POST',
        WEBHOOK_URL,
        body=encoded_msg,
        headers={'Content-Type': 'application/json'}
    )
    return resp.status


def lambda_handler(event, context):
    """
    Função acionada por um alarme do CloudWatch via SNS.
    Envia uma notificação formatada para o Discord/Slack.
    """
    logger.info(f"Evento recebido: {json.dumps(event)}")

    # Validação antecipada: garante que o WEBHOOK_URL está configurado
    if not WEBHOOK_URL:
        logger.error("Variável de ambiente WEBHOOK_URL não configurada.")
        return {
            'statusCode': 500,
            'body': json.dumps('Erro: WEBHOOK_URL não configurada.')
        }

    try:
        # Extrai e valida a estrutura do evento SNS
        records = event.get('Records', [])
        if not records:
            raise ValueError("Evento SNS sem 'Records'.")

        sns_record = records[0].get('Sns', {})
        raw_message = sns_record.get('Message')
        if not raw_message:
            raise ValueError("Campo 'Message' ausente no registro SNS.")

        sns_message = json.loads(raw_message)

        alarm_name  = sns_message.get('AlarmName', 'Alarme Desconhecido')
        new_state   = sns_message.get('NewStateValue', 'ESTADO_DESCONHECIDO')
        reason      = sns_message.get('NewStateReason', 'Sem motivo especificado')
        instance_id = get_instance_id(sns_message)

        payload     = build_discord_payload(alarm_name, new_state, reason, instance_id)
        status_code = send_webhook(payload)

        logger.info(f"Resposta do Webhook: {status_code}")

        # Trata respostas de erro do Discord/Slack (ex: 400, 401, 429)
        if status_code not in (200, 204):
            logger.warning(f"Webhook retornou status inesperado: {status_code}")
            return {
                'statusCode': status_code,
                'body': json.dumps(f'Webhook retornou status {status_code}.')
            }

        return {
            'statusCode': 200,
            'body': json.dumps('Notificação enviada com sucesso!')
        }

    except (KeyError, ValueError, json.JSONDecodeError) as e:
        logger.error(f"Erro ao processar evento SNS: {str(e)}")
        return {
            'statusCode': 400,
            'body': json.dumps(f'Erro no formato do evento: {str(e)}')
        }

    except Exception as e:
        logger.error(f"Erro inesperado: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps(f'Erro interno: {str(e)}')
        }
