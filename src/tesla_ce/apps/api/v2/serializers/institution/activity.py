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
""" Activity serializer module """
from rest_framework import serializers
from django.shortcuts import get_object_or_404

from tesla_ce.models import Activity, Learner

from .course import InstitutionCourseSerializer
from .activity_instrument import InstitutionCourseActivityInstrumentSerializer


class InstitutionCourseActivitySerializer(serializers.ModelSerializer):
    """Activity serialize model module."""
    course_id = serializers.ReadOnlyField()
    vle_id = serializers.ReadOnlyField()
    vle_activity_type = serializers.ReadOnlyField()
    vle_activity_id = serializers.ReadOnlyField()
    name = serializers.ReadOnlyField()
    start = serializers.ReadOnlyField()
    end = serializers.ReadOnlyField()
    description = serializers.ReadOnlyField()

    class Meta:
        model = Activity
        exclude = ["vle", "course"]


class InstitutionCourseActivityExtendedSerializer(serializers.ModelSerializer):
    """ Activity extended serialize model module. """
    vle_id = serializers.ReadOnlyField()
    vle_activity_type = serializers.ReadOnlyField()
    vle_activity_id = serializers.ReadOnlyField()
    name = serializers.ReadOnlyField()
    start = serializers.ReadOnlyField()
    end = serializers.ReadOnlyField()
    description = serializers.ReadOnlyField()
    course = InstitutionCourseSerializer(read_only=True)
    instruments = InstitutionCourseActivityInstrumentSerializer(source='configuration', read_only=True, many=True)
    user_instruments = serializers.SerializerMethodField()

    class Meta:
        model = Activity
        exclude = ["vle"]

    def get_user_instruments(self, instance):
        """ Instruments for current user """
        learner = self.context['request'].user.learner
        return InstitutionCourseActivityInstrumentSerializer(
            instance.get_learner_instruments(learner), many=True).data


class InstitutionUserActivityExtendedSerializer(InstitutionCourseActivityExtendedSerializer):

    def get_user_instruments(self, instance):
        """ Instruments for current user """
        user_id = self.context['request'].parser_context['kwargs']['pk']
        try:
            learner = instance.course.learners.get(pk=user_id)
            instruments = instance.get_learner_instruments(learner)
        except Learner.DoesNotExist:
            instruments = []
        return InstitutionCourseActivityInstrumentSerializer(instruments, many=True).data
