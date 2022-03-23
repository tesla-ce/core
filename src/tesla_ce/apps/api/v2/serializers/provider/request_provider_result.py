#  Copyright (c) 2020 Xavier Baró
#
#      This program is free software: you can redistribute it and/or modify
#      it under the terms of the GNU Affero General Public License as
#      published by the Free Software Foundation, either version 3 of the
#      License, or (at your option) any later version.
#
#      This program is distributed in the hope that it will be useful,
#      but WITHOUT ANY WARRANTY; without even the implied warranty of
#      MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#      GNU Affero General Public License for more details.
#
#      You should have received a copy of the GNU Affero General Public License
#      along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""RequestResult api serialize module."""
import simplejson
from django.core.files.base import ContentFile
from django.db.models import Q

from rest_framework import serializers

from tesla_ce import tasks
from tesla_ce.apps.api.utils import JSONField
from tesla_ce.models import Request
from tesla_ce.models import RequestProviderResult


class ProviderVerificationRequestSerializer(serializers.ModelSerializer):
    """Provider Request serialize model module."""

    id = serializers.IntegerField(read_only=True)
    data = serializers.FileField(read_only=True)

    class Meta:
        model = Request
        fields = ["id", "data"]


class ProviderVerificationRequestResultSerializer(serializers.ModelSerializer):

    request = ProviderVerificationRequestSerializer(read_only=True)
    learner_id = serializers.UUIDField(source='request.learner.learner_id', read_only=True)
    audit = serializers.FileField(read_only=True)
    audit_data = JSONField(required=False, write_only=True, allow_null=True, default=None)

    """Provider RequestResult serialize model module."""
    class Meta:
        model = RequestProviderResult
        fields = ["id", "request", "learner_id", "result", "status", "error_message", "code", "audit", "audit_data"]

    def update(self, instance, validated_data):
        new_instance = super().update(instance, validated_data)
        new_instance.audit.save('{}__audit.json'.format(new_instance.request.data.name),
                                ContentFile(simplejson.dumps(new_instance.audit_data).encode('utf-8')))

        # If all the providers reported their results, launch summarise task
        if RequestProviderResult.objects.filter(Q(status=0) | Q(status=7),
                                                request_id=new_instance.request_id,
                                                provider__instrument=new_instance.provider.instrument
                                                ).count() == 0:
            tasks.requests.verification.create_verification_summary.apply_async((
                    instance.request.id,
                    new_instance.provider.instrument_id,
            ))
        return new_instance
