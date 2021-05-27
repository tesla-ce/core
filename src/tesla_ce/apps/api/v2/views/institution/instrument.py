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
""" Instrument views module """
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets
from rest_framework.filters import OrderingFilter
from rest_framework.filters import SearchFilter

from tesla_ce.apps.api.v2.serializers import InstrumentSerializer
from tesla_ce.models import Instrument


# pylint: disable=too-many-ancestors
class InstitutionInstrumentViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint that allows read instrument data
    """
    queryset = Instrument.objects.filter(enabled=True).order_by('acronym')
    serializer_class = InstrumentSerializer
    filter_backends = [SearchFilter, DjangoFilterBackend, OrderingFilter]
    # TODO: Filter instruments allowed by institution (new feature)
    '''
    filterset_fields = ['activity_type', 'external_token', 'description', 'conf', 'vle']
    search_fields = ['activity_type', 'external_token', 'description', 'conf', 'vle']
    '''
