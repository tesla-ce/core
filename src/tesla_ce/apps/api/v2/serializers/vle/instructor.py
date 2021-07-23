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
"""Instructor api serialize module."""
from django.utils import timezone

from rest_framework import exceptions
from rest_framework import serializers

from tesla_ce.models import Course
from tesla_ce.models import InstitutionUser
from tesla_ce.models import Instructor
from tesla_ce.models import User


class VLECourseInstructorSerializer(serializers.ModelSerializer):
    """Instructor serialize model module."""

    username = serializers.CharField(read_only=True)
    last_login = serializers.DateTimeField(read_only=True)
    first_name = serializers.CharField(required=False, default=None)
    last_name = serializers.CharField(required=False, default=None)
    email = serializers.EmailField(required=False, default=None)
    institution_id = serializers.HiddenField(default=None)

    class Meta:
        model = Instructor
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
                    'Instructor does not exist and information to create it is not provided'
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
            instructor = Instructor.objects.get(institution=institution, uid=attrs['uid'])
            validated_data = super().validate(attrs)
        except Instructor.DoesNotExist:
            # Check if institution allows to create new instructors
            if institution.disable_vle_instructor_creation:
                raise exceptions.NotFound('Instructor not found')

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

            # Create the instructor object
            instructor = Instructor(institutionuser_ptr=inst_user, institution_id=attrs['institution_id'])
            instructor.save_base(raw=True)
            instructor = Instructor.objects.get(id=inst_user.id)

            # Apply validators
            validated_data = super().validate(attrs)

        # Store the objects
        validated_data['instructor'] = instructor
        validated_data['course'] = course

        return validated_data

    def create(self, validated_data):
        """
            Create a new instructor in the course
            :param validated_data: Validated data
            :return: New instance
        """
        instructor = None
        if 'instructor' in validated_data:
            instructor = validated_data['instructor']
        if instructor is None:
            raise exceptions.ValidationError('Error creating instructor')
        validated_data['course'].instructors.add(instructor)
        return instructor
