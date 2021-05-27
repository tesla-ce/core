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
""" InformedConsent views module """
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.filters import OrderingFilter
from rest_framework.filters import SearchFilter
from rest_framework.views import Response
from rest_framework.views import status
from rest_framework_extensions.mixins import NestedViewSetMixin

from tesla_ce.apps.api.v2.serializers import InstitutionInformedConsentSerializer
from tesla_ce.models import InformedConsent
from tesla_ce.models import Institution
from tesla_ce.models.informed_consent import get_current_ic_version


# pylint: disable=too-many-ancestors
class InstitutionInformedConsentViewSet(viewsets.ModelViewSet, NestedViewSetMixin):
    """
    API endpoint that allows activity to be viewed or edited.
    """
    serializer_class = InstitutionInformedConsentSerializer
    filter_backends = [SearchFilter, DjangoFilterBackend, OrderingFilter]
    '''
    filterset_fields = ['activity_type', 'external_token', 'description', 'conf', 'vle']
    search_fields = ['activity_type', 'external_token', 'description', 'conf', 'vle']
    '''

    def get_queryset(self):
        queryset = InformedConsent.objects
        if 'parent_lookup_institution_id' in self.kwargs:
            queryset = queryset.filter(
                institution__id=self.kwargs['parent_lookup_institution_id']
            )
        return queryset.all().order_by('id')

    @action(detail=False, methods=['GET'])
    def current(self, request, *args, **kwargs):
        """
            Retrieve the current informed consent
        """
        try:
            institution = Institution.objects.get(id=kwargs['parent_lookup_institution_id'])
        except Institution.DoesNotExist:
            return Response('Invalid institution', status=status.HTTP_404_NOT_FOUND)
        try:
            current_ic = InformedConsent.objects.get(version=get_current_ic_version(institution),
                                                     institution_id=kwargs['parent_lookup_institution_id'])
        except InformedConsent.DoesNotExist:
            return Response('Invalid version', status=status.HTTP_404_NOT_FOUND)

        serializer = self.get_serializer(current_ic)
        return Response(serializer.data)
