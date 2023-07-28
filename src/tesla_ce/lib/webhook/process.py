import json
import simplejson
from django.core.files.base import ContentFile
from tesla_ce.models.provider import Provider
from tesla_ce.models.webhooks import WebhookMessage
from tesla_ce.models.request import Request
from tesla_ce.models.request_provider_result import RequestProviderResult


def process_webhook_message(message_id, provider_id):
    webhook_message = WebhookMessage.objects.get(pk=message_id)
    provider = Provider.objects.get(pk=provider_id)

    if provider.acronym == 'tpt':
        process_webhook_message_tpt(webhook_message, provider)


def process_webhook_message_tpt(webhook_message, provider):
    body = json.loads(webhook_message.body)

    if body['action'] == 'UPDATE_RESULT':
        request = Request.objects.get(pk=body['request_id'])
        request_provider_result = RequestProviderResult.objects.get(provider=provider, request=request)
        request_provider_result.result = float(body['result'])
        request_provider_result.audit_data = body['audit_data']
        # status processed
        request_provider_result.status = 1
        request_provider_result.code = body['code']
        request_provider_result.audit.save('{}__audit.json'.format(request_provider_result.request.data.name),
                                ContentFile(simplejson.dumps(request_provider_result.audit_data).encode('utf-8')))

        request_provider_result.save()
