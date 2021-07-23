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
"""Course Learner api serialize module."""
from rest_framework import serializers

from tesla_ce.models import Learner
from tesla_ce.models import Course
from .institution import InstitutionSerializer
from .learner import InstitutionLearnerConsentSerializer


class InstitutionCourseLearnerSerializer(serializers.ModelSerializer):
    """Course Learner serialize model module."""

    institution = InstitutionSerializer(read_only=True)
    username = serializers.CharField(read_only=True)
    uid = serializers.CharField()
    first_name = serializers.CharField(read_only=True)
    last_name = serializers.CharField(read_only=True)
    locale = serializers.CharField(read_only=True)
    consent = InstitutionLearnerConsentSerializer(read_only=True, allow_null=True, default=None)
    consent_accepted = serializers.DateTimeField(read_only=True)
    consent_rejected = serializers.DateTimeField(read_only=True)
    learner_id = serializers.UUIDField(read_only=True)
    last_login = serializers.DateTimeField(read_only=True)
    send = serializers.JSONField(read_only=True)
    email = serializers.EmailField(read_only=True)
    institution_id = serializers.HiddenField(default=None, allow_null=True)
    course_id = serializers.HiddenField(default=None, allow_null=True)
    ic_status = serializers.CharField(read_only=True)
    login_allowed = serializers.BooleanField(read_only=True, allow_null=False, default=False)

    class Meta:
        model = Learner
        exclude = ["password", "is_superuser", "is_staff", "is_active", "date_joined", "groups", "user_permissions",
                   "inst_admin", "send_admin", "legal_admin", "data_admin"]

    def validate(self, attrs):
        """
            Validate the given attributes
            :param attrs: Attributes parsed from request
            :type attrs: dict
            :return: Validated attributes
            :rtype: dict
        """
        # Add predefined fields
        attrs['institution_id'] = self.context['view'].kwargs['parent_lookup_vle__institution_id']
        attrs['course_id'] = self.context['view'].kwargs['parent_lookup_id']

        # Apply validators
        for validator in self.get_validators():
            validator(attrs, self)
        return super().validate(attrs)
