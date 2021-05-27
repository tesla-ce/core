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
""" Read Only Institution views module """
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets
from rest_framework.filters import OrderingFilter
from rest_framework.filters import SearchFilter
from rest_framework.mixins import ListModelMixin
from rest_framework.mixins import UpdateModelMixin
from rest_framework_extensions.mixins import NestedViewSetMixin

from tesla_ce.apps.api import permissions
from tesla_ce.apps.api.v2.serializers import InstitutionSerializer
from tesla_ce.models import Institution


# pylint: disable=too-many-ancestors
class InstitutionViewSet(viewsets.ReadOnlyModelViewSet, NestedViewSetMixin, ListModelMixin, UpdateModelMixin):
    """
    API endpoint that allows access to institution data.
    """
    model = Institution
    permission_classes = [
        permissions.InstitutionAdminPermission |
        permissions.InstitutionMemberReadOnlyPermission |
        permissions.GlobalAdminReadOnlyPermission
    ]
    serializer_class = InstitutionSerializer
    filter_backends = [SearchFilter, DjangoFilterBackend, OrderingFilter]
    lookup_url_kwarg = 'institution_id'

    filterset_fields = ['acronym', 'name']
    search_fields = ['acronym', 'name']

    def get_queryset(self):
        qs = Institution.objects.all().order_by('created_at')
        if not self.request.user.is_staff:
            qs.filter(id=self.request.user.institution.id)
        return qs
