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
from django.utils import timezone
from rest_framework import exceptions
from rest_framework import serializers

from tesla_ce.models import Course
from tesla_ce.models import InformedConsent
from tesla_ce.models import InstitutionUser
from tesla_ce.models import Learner
from tesla_ce.models import User


class VLECourseLearnerConsentSerializer(serializers.ModelSerializer):
    """Learner Informed Consent serialize model module."""

    status = serializers.CharField(read_only=True)

    class Meta:
        model = InformedConsent
        fields = ["version", "status"]


class VLECourseLearnerSerializer(serializers.ModelSerializer):
    """Learner serialize model module."""

    username = serializers.CharField(read_only=True)
    consent = VLECourseLearnerConsentSerializer(read_only=True, allow_null=True, default=None)
    consent_accepted = serializers.DateTimeField(read_only=True)
    consent_rejected = serializers.DateTimeField(read_only=True)
    learner_id = serializers.UUIDField(read_only=True)
    last_login = serializers.DateTimeField(read_only=True)
    send = serializers.JSONField(read_only=True)
    ic_status = serializers.CharField(read_only=True)
    enrolment_status = serializers.JSONField(read_only=True)

    first_name = serializers.CharField(required=False, default=None)
    last_name = serializers.CharField(required=False, default=None)
    email = serializers.EmailField(required=False, default=None)
    institution_id = serializers.HiddenField(default=None)

    class Meta:
        model = Learner
        exclude = ["password", "is_superuser", "is_staff", "is_active", "date_joined", "groups",
                   "user_permissions", "institution", "login_allowed"]

    @staticmethod
    def _create_institution_user(attrs):
        """
            Create an institution user for given attributes
            :param attrs: Attributes for the new institution user
            :type attrs: dict

            :return: Institution user
            :rtype: InstitutionUser
        """
        # Check if the user exists
        try:
            # Create using existing user
            user = User.objects.get(email=attrs['email'])
            inst_user = InstitutionUser(user_ptr=user, institution_id=attrs['institution_id'])
            inst_user.created_at = timezone.now()
            inst_user.updated_at = timezone.now()
            inst_user.save_base(raw=True)
            inst_user = InstitutionUser.objects.get(id=inst_user.id)
        except User.DoesNotExist:
            # Create a new user
            if attrs['first_name'] is None or attrs['last_name'] is None or attrs['email'] is None:
                raise exceptions.ValidationError(
                    'Learner does not exist and information to create it is not provided'
                )
            attrs['username'] = attrs['email']
            inst_user = InstitutionUser.objects.create(**attrs)
            inst_user.save()
            inst_user = InstitutionUser.objects.get(id=inst_user.id)
        return inst_user

    def validate(self, attrs):
        """
            Validate the given attributes
            :param attrs: Attributes parsed from request
            :type attrs: dict
            :return: Validated attributes
            :rtype: dict
        """
        # Get related objects
        try:
            course = Course.objects.get(id=self.context['view'].kwargs['parent_lookup_course_id'])
            institution = course.vle.institution
            attrs['institution_id'] = institution.id
        except Course.DoesNotExist:
            raise exceptions.NotFound('Course not found')

        try:
            learner = Learner.objects.get(institution=institution, uid=attrs['uid'])
            validated_data = super().validate(attrs)
        except Learner.DoesNotExist:
            # Check if institution allows to create new learners
            if institution.disable_vle_learner_creation:
                raise exceptions.NotFound('Learner not found')

            # Search in institution users
            try:
                inst_user = InstitutionUser.objects.get(institution_id=attrs['institution_id'], uid=attrs['uid'])
            except InstitutionUser.DoesNotExist:
                inst_user = None

            # If does not exist, try to create
            if inst_user is None:
                if institution.disable_vle_user_creation:
                    # User creation is not allowed
                    raise exceptions.NotFound('User not found')
                inst_user = self._create_institution_user(attrs)

            if inst_user is None:
                raise exceptions.ValidationError('Error creating new associated user')

            # Create the learner object
            learner = Learner(institutionuser_ptr=inst_user,
                              institution_id=attrs['institution_id'],
                              joined_at=timezone.now())
            learner.save_base(raw=True)
            learner = Learner.objects.get(id=inst_user.id)

            # Apply validators
            validated_data = super().validate(attrs)

        # Store the objects
        validated_data['learner'] = learner
        validated_data['course'] = course

        return validated_data

    def create(self, validated_data):
        """
            Create a new learner in the course
            :param validated_data: Validated data
            :return: New instance
        """
        learner = None
        if 'learner' in validated_data:
            learner = validated_data['learner']
        if learner is None:
            raise exceptions.ValidationError('Error creating learner')
        validated_data['course'].learners.add(learner)
        return learner


class VLECourseActivityLearnerSerializer(serializers.ModelSerializer):
    """Learner serialize model module."""

    class Meta:
        model = Learner
        fields = ['id', 'first_name', 'last_name', 'email', 'uid', 'institution_id', 'learner_id']
