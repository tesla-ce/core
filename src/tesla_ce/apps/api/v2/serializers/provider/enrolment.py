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
""" Provider enrolment serializers module """
from django.core.files.base import ContentFile
from django.db import transaction
from django.utils import timezone
from rest_framework import serializers

from tesla_ce.models import Enrolment
from tesla_ce.models import Learner
from tesla_ce.models.enrolment import get_upload_path


class ProviderEnrolmentSerializer(serializers.ModelSerializer):
    """Enrolment sample serialize class."""

    learner_id = serializers.UUIDField(source='learner.learner_id')
    model = serializers.FileField(read_only=True)
    task_id = serializers.UUIDField(write_only=True, allow_null=False)
    is_locked = serializers.BooleanField(read_only=True)
    model_upload_url = serializers.SerializerMethodField(read_only=True)
    percentage = serializers.FloatField(required=False, allow_null=None, default=0)
    can_analyse = serializers.BooleanField(required=False, allow_null=None, default=False)
    model_total_samples = serializers.IntegerField(read_only=True)
    used_samples = serializers.ListField(write_only=True, allow_null=True, allow_empty=True, required=False, default=[],
                                         child=serializers.IntegerField())

    class Meta:
        model = Enrolment
        fields = ['id', 'learner_id', 'model', 'is_locked', 'task_id', 'model_upload_url', 'percentage',
                  'can_analyse', 'model_total_samples', 'used_samples']

    def get_model_upload_url(self, instance):
        if not self.context['request'].method == 'POST':
            return None
        pre_post = instance.model.storage.bucket.meta.client.generate_presigned_post(
            Bucket=instance.model.storage.bucket.name,
            Key=get_upload_path(instance, None)
        )

        """
        TODO: Move to presigned URL  => Check: https://boto3.amazonaws.com/v1/documentation/api/1.9.42/guide/s3.html#generating-presigned-urls
        params = {
            'Bucket': instance.model.storage.bucket.name,
            'Key': get_upload_path(instance, None)
        }
        url = instance.model.storage.bucket.meta.client.generate_presigned_url(
            'put_object', Params=params
        )
        """

        return pre_post

    def validate_learner_id(self, value):
        """
            Validate the provided learner UUID ID
            :param value: Learner UUID ID
            :type value: str
            :return: Validated value
            :rtype: str
        """
        try:
            learner = Learner.objects.get(learner_id=value)
        except Learner.DoesNotExist:
            raise serializers.ValidationError('Invalid learner')
        return learner.id

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
        attrs['learner_id'] = attrs['learner']['learner_id']

        # Check if model exists
        with transaction.atomic():
            # Get current model or create a new one
            try:
                model = Enrolment.objects.get(provider_id=attrs['provider_id'], learner_id=attrs['learner_id'])
            except Enrolment.DoesNotExist:
                model = Enrolment.objects.create(
                    provider_id=attrs['provider_id'],
                    learner_id=attrs['learner_id'],
                    percentage=0,
                    can_analyse=False
                )
                model.model.save(get_upload_path(model, None),  ContentFile('{}'.encode('utf-8')))
            # Check if model is locked
            if model.is_locked and str(model.locked_by) != str(attrs['task_id']):
                # If model lock have more than 5 hours, release previous lock
                time_threshold = timezone.now() - timezone.timedelta(hours=5)
                if model.locked_at >= time_threshold:
                    raise serializers.ValidationError('Model is locked')

            # Lock the model
            model.locked_by = attrs['task_id']
            model.locked_at = timezone.now()
            model.save()

            # Set model as current instance
            self.instance = model

        return super().validate(attrs)

    def update(self, instance, validated_data):
        if self.context['request'].method == 'PUT':
            # Update model metadata and unlock it
            if 'percentage' in validated_data:
                instance.percentage = validated_data['percentage']
            if 'can_analyse' in validated_data:
                instance.can_analyse = validated_data['can_analyse']
            if 'used_samples' in validated_data:
                # Update existing samples in validation
                instance.model_samples.set(validated_data['used_samples'])

            instance.locked_at = None
            instance.locked_by = None
            instance.save()
        return instance
