#  Copyright (c) 2020 Roger Muñoz
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
"""Request api serialize module."""
from rest_framework import serializers

from tesla_ce.models import Request
from tesla_ce.models import RequestResult


class InstitutionCourseActivityReportRequestResultSerializer(serializers.ModelSerializer):
    """ Request result model serializer """
    class Meta:
        model = RequestResult
        fields = "__all__"


class InstitutionCourseActivityReportRequestSerializer(serializers.ModelSerializer):
    """ Learner Request serializer model """
    result = InstitutionCourseActivityReportRequestResultSerializer(source="requestresult_set", many=True)

    class Meta:
        model = Request
        fields = "__all__"
