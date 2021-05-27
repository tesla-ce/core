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
""" InformedConsentDocument views module """
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets
from rest_framework.filters import OrderingFilter
from rest_framework.filters import SearchFilter
from rest_framework_extensions.mixins import NestedViewSetMixin

from tesla_ce.apps.api.v2.serializers import InstitutionInformedConsentDocumentSerializer
from tesla_ce.models import InformedConsentDocument


# pylint: disable=too-many-ancestors
class InstitutionInformedConsentDocumentViewSet(viewsets.ModelViewSet, NestedViewSetMixin):
    """
    API endpoint that allows activity to be viewed or edited.
    """
    serializer_class = InstitutionInformedConsentDocumentSerializer
    filter_backends = [SearchFilter, DjangoFilterBackend, OrderingFilter]
    lookup_field = 'language'
    '''
    filterset_fields = ['activity_type', 'external_token', 'description', 'conf', 'vle']
    search_fields = ['activity_type', 'external_token', 'description', 'conf', 'vle']
    '''

    def get_queryset(self):
        queryset = InformedConsentDocument.objects
        if 'parent_lookup_institution_id' in self.kwargs and 'parent_lookup_informed_consent_id' in self.kwargs:
            queryset = queryset.filter(
                consent__institution__id=self.kwargs['parent_lookup_institution_id'],
                consent_id=self.kwargs['parent_lookup_informed_consent_id']
            )
        return queryset.all().order_by('id')
