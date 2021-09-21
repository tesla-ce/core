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
"""SENDLearner api serialize module."""
from rest_framework import serializers

from tesla_ce.models import SENDLearner
from .send_category import InstitutionSENDCategorySerializer


class InstitutionSENDLearnerSerializer(serializers.ModelSerializer):
    """SENDLearner serialize model module."""

    learner_id = serializers.HiddenField(default=None, allow_null=True)
    info = InstitutionSENDCategorySerializer(source='category', read_only=True, many=False)

    class Meta:
        model = SENDLearner
        fields = ["id", "expires_at", "category", "learner_id", "info"]
        validators = [serializers.UniqueTogetherValidator(
            queryset=SENDLearner.objects.all(),
            fields=['learner_id', 'category']
        ),]

    def validate(self, attrs):
        """
            Validate the given attributes
            :param attrs: Attributes parsed from request
            :type attrs: dict
            :return: Validated attributes
            :rtype: dict
        """
        # Add predefined fields
        attrs['learner_id'] = self.context['view'].kwargs['parent_lookup_learner_id']
        # Apply validators
        for validator in self.get_validators():
            validator(attrs, self)
        return super().validate(attrs)
