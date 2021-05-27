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
"""Learner api serialize module."""
from rest_framework import serializers
from rest_framework import validators

from tesla_ce.apps.api.utils import BodySerializer
from tesla_ce.models import InformedConsent
from tesla_ce.models import Institution
from tesla_ce.models import InstitutionUser
from tesla_ce.models import Learner
from tesla_ce.models import User
from .institution import InstitutionSerializer


class InstitutionLearnerConsentSerializer(serializers.ModelSerializer):
    """Learner Informed Consent serialize model module."""

    status = serializers.CharField(read_only=True)

    class Meta:
        model = InformedConsent
        fields = ["version", "status"]


class InstitutionLearnerSerializer(serializers.ModelSerializer):
    """Learner serialize model module."""

    institution = InstitutionSerializer(read_only=True)
    username = serializers.CharField(read_only=True,
                                     validators=[
                                         validators.UniqueValidator(queryset=User.objects.all())
                                     ])
    consent = InstitutionLearnerConsentSerializer(read_only=True, allow_null=True, default=None)
    consent_accepted = serializers.DateTimeField(read_only=True)
    consent_rejected = serializers.DateTimeField(read_only=True)
    learner_id = serializers.UUIDField(read_only=True)
    last_login = serializers.DateTimeField(read_only=True)
    send = serializers.JSONField(read_only=True)
    email = serializers.EmailField(validators=[
        validators.UniqueValidator(queryset=User.objects.all())
    ])
    institution_id = serializers.HiddenField(default=None, allow_null=True)
    ic_status = serializers.CharField(read_only=True)
    login_allowed = serializers.BooleanField(read_only=True, allow_null=False, default=False)

    class Meta:
        model = Learner
        exclude = ["password", "is_superuser", "is_staff", "is_active", "date_joined", "groups", "user_permissions"]
        validators = [serializers.UniqueTogetherValidator(
            queryset=InstitutionUser.objects.all(),
            fields=['institution_id', 'uid']
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
        attrs['institution_id'] = self.context['view'].kwargs['parent_lookup_institution_id']
        attrs['username'] = attrs['email']

        # Apply validators
        for validator in self.get_validators():
            validator(attrs, self)
        return super().validate(attrs)

    def validate_email(self, value):
        """
            Validate the given email
            :param value: Email for the learner
            :type value: str
            :return: Validated value
            :rtype: str
        """
        try:
            institution = Institution.objects.get(id=self.context['view'].kwargs['parent_lookup_institution_id'])
        except Institution.DoesNotExist:
            raise serializers.ValidationError('Invalid institution')
        if institution.mail_domain is not None and len(institution.mail_domain) > 0 \
                and not value.endswith(institution.mail_domain):
            raise serializers.ValidationError('Provided email does not belong to institution domain')
        return value

    def create(self, validated_data):
        """
            Create a new instance from provided data

            :param validated_data: Validated data from request
            :return: Created instance
            :rtype: Learner
        """
        instance = super().create(validated_data)
        instance.set_unusable_password()
        instance.save()
        return instance


class InstitutionLearnerICBodySerializer(BodySerializer):
    """ Body parser for Informed Consent acceptance """
    version = serializers.CharField(required=True)


class InstitutionLearnerDetailSerializer(InstitutionLearnerSerializer):
    enrolment_status = serializers.JSONField(read_only=True)

