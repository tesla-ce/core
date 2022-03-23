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
""" Provider enrolment sample validation serializers module """
import json

from django.core.files.base import ContentFile
from rest_framework import serializers

from tesla_ce.apps.api.utils import JSONField
from tesla_ce.models import EnrolmentSampleValidation
from tesla_ce.tasks.requests.enrolment import create_validation_summary
from .enrolment_sample import ProviderEnrolmentSampleSerializer


class ProviderEnrolmentSampleValidationSerializer(serializers.ModelSerializer):
    """Enrolment sample validation serialize class."""

    sample_id = serializers.HiddenField(default=None)
    provider_id = serializers.HiddenField(default=None)
    provider = serializers.IntegerField(read_only=True, source="provider_id")
    sample = ProviderEnrolmentSampleSerializer(read_only=True)
    validation_info = JSONField(write_only=True, allow_null=True, default=None)
    info = serializers.FileField(read_only=True, allow_null=True, default=None)
    message_code_id = serializers.CharField(allow_null=True, default=None)
    contribution = serializers.FloatField(allow_null=True, default=None)

    class Meta:
        model = EnrolmentSampleValidation
        fields = ["id", "status", "info", "validation_info", "sample_id", "provider_id", "provider",
                  "sample", "error_message", "contribution", "message_code_id"]
        validators = [serializers.UniqueTogetherValidator(
            queryset=EnrolmentSampleValidation.objects.all(),
            fields=['sample_id', 'provider_id']
        ), ]

    def validate(self, attrs):
        """
            Validate the given attributes
            :param attrs: Attributes parsed from request
            :type attrs: dict
            :return: Validated attributes
            :rtype: dict
        """
        # Add predefined fields
        attrs['provider_id'] = self.context['view'].kwargs['parent_lookup_provider_id']
        attrs['sample_id'] = self.context['view'].kwargs['parent_lookup_sample_id']

        # Apply validators
        for validator in self.get_validators():
            validator(attrs, self)
        return super().validate(attrs)

    def update(self, instance, validated_data):
        """
            Update an enrolment sample validation
            :param instance: Current instance
            :type instance: EnrolmentSampleValidation
            :param validated_data: Validated data
            :type validated_data: dict
            :return: New instance
        """
        if validated_data['validation_info'] is None and instance.info is not None and len(instance.info.name) > 0:
            instance.info.delete()
        if validated_data['validation_info'] is not None:
            instance.info.save('{}.validation.{}'.format(instance.sample.data.name, instance.id),
                               ContentFile(json.dumps(validated_data['validation_info']).encode('utf-8')))
        new_instance = super().update(instance, validated_data)

        if 0 < new_instance.status < 4:
            create_validation_summary.apply_async((new_instance.sample.learner.learner_id, new_instance.sample_id,))

        return new_instance
