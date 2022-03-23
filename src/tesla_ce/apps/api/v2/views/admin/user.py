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
#
""" User views module """
from django.db.models import Q
from django_filters import rest_framework as filters_dj
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets
from rest_framework.filters import OrderingFilter
from rest_framework.filters import SearchFilter

from tesla_ce.apps.api import permissions
from tesla_ce.apps.api.v2.serializers import UserSerializer
from tesla_ce.models import Institution
from tesla_ce.models import User


def institution_values():
    """ Get available institutions for filter """
    institutions = Institution.objects.all()
    return ((inst.id, inst.acronym) for inst in institutions)


def roles_values():
    """ Get available roles for filter """
    return (
        ('GLOBAL_ADMIN', 'GLOBAL_ADMIN'),
        ('ADMIN', 'ADMIN'),
        ('SEND', 'SEND'),
        ('LEGAL', 'LEGAL'),
        ('DATA', 'DATA'),
        # ('INSTRUCTOR', 'INSTRUCTOR'),
        # ('LEARNER', 'LEARNER'),
    )


class UserFilter(filters_dj.FilterSet):
    """ Filter implementation for Users """
    institution = filters_dj.ChoiceFilter(field_name="institution",
                                          label="institution",
                                          choices=institution_values,
                                          null_label='None',
                                          null_value=-1,
                                          method='filter_institution')

    roles = filters_dj.MultipleChoiceFilter(field_name="roles",
                                            label="roles",
                                            choices=roles_values,
                                            method='filter_roles')

    username = filters_dj.CharFilter(lookup_expr='icontains')
    first_name = filters_dj.CharFilter(lookup_expr='icontains')
    last_name = filters_dj.CharFilter(lookup_expr='icontains')
    email = filters_dj.CharFilter(lookup_expr='icontains')

    def filter_institution(self, queryset, name, value):

        # Get the value
        value = int(value)

        # Request users with no institution assigned
        if value < 0:
            return queryset.filter(institutionuser=None)

        # Filter by provided institution
        return queryset.filter(institutionuser__institution=value)

    def filter_roles(self, queryset, name, value):

        # No filter provided
        if value is None or len(value) == 0:
            return queryset

        # Filter by provided roles
        filter_q = Q()
        if 'GLOBAL_ADMIN' in value:
            filter_q = filter_q | Q(is_staff=True)
        if 'ADMIN' in value:
            filter_q = filter_q | Q(institutionuser__inst_admin=True)
        if 'SEND' in value:
            filter_q = filter_q | Q(institutionuser__send_admin=True)
        if 'LEGAL' in value:
            filter_q = filter_q | Q(institutionuser__legal_admin=True)
        if 'DATA' in value:
            filter_q = filter_q | Q(institutionuser__data_admin=True)
        return queryset.filter(filter_q)

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'institution', 'roles']


# pylint: disable=too-many-ancestors
class AdminUserViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    model = User
    serializer_class = UserSerializer
    permission_classes = [permissions.GlobalAdminPermission]
    filter_backends = [SearchFilter, DjangoFilterBackend, OrderingFilter]
    filterset_class = UserFilter
    search_fields = ['username', 'first_name', 'last_name', 'email']

    def get_queryset(self):
        queryset = User.objects
        return queryset.all().order_by('id')
