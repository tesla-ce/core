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
""" Institution User views module """
from django.db.models import Q
from django_filters import rest_framework as filters_dj
from django_filters.rest_framework import DjangoFilterBackend
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied
from rest_framework.views import Response
from rest_framework.filters import OrderingFilter
from rest_framework.filters import SearchFilter
from rest_framework_extensions.mixins import NestedViewSetMixin

from tesla_ce.apps.api import permissions
from tesla_ce.apps.api.v2.serializers import InstitutionUserSerializer
from tesla_ce.apps.api.v2.serializers import InstitutionCourseActivityExtendedSerializer
from tesla_ce.models import InstitutionUser
from tesla_ce.models import Activity
from tesla_ce.models.user import get_institution_user
from tesla_ce.models.user import is_global_admin


def roles_values():
    """ Get available roles for filter """
    return (
        ('ADMIN', 'ADMIN'),
        ('SEND', 'SEND'),
        ('LEGAL', 'LEGAL'),
        ('DATA', 'DATA'),
        ('INSTRUCTOR', 'INSTRUCTOR'),
        ('LEARNER', 'LEARNER'),
    )


class InstitutionUserFilter(filters_dj.FilterSet):
    """ Filter implementation for Institution Users """

    roles = filters_dj.MultipleChoiceFilter(field_name="roles",
                                            label="roles",
                                            choices=roles_values,
                                            method='filter_roles')

    username = filters_dj.CharFilter(lookup_expr='icontains')
    first_name = filters_dj.CharFilter(lookup_expr='icontains')
    last_name = filters_dj.CharFilter(lookup_expr='icontains')
    email = filters_dj.CharFilter(lookup_expr='icontains')
    uid = filters_dj.CharFilter(lookup_expr='icontains')

    def filter_roles(self, queryset, name, value):

        # No filter provided
        if value is None or len(value) == 0:
            return queryset

        # Filter by provided roles
        filter_q = Q()
        if 'ADMIN' in value:
            filter_q = filter_q | Q(inst_admin=True)
        if 'SEND' in value:
            filter_q = filter_q | Q(send_admin=True)
        if 'LEGAL' in value:
            filter_q = filter_q | Q(legal_admin=True)
        if 'DATA' in value:
            filter_q = filter_q | Q(data_admin=True)
        if 'LEARNER' in value:
            filter_q = filter_q | Q(learner__isnull=False)
        if 'INSTRUCTOR' in value:
            filter_q = filter_q | Q(instructor__isnull=False)
        return queryset.filter(filter_q)

    class Meta:
        model = InstitutionUser
        fields = ['username', 'first_name', 'last_name', 'email', 'roles', 'uid']


# pylint: disable=too-many-ancestors
class InstitutionUserViewSet(NestedViewSetMixin, viewsets.ModelViewSet):
    """
    API endpoint that allow institution users to be managed.
    """
    model = InstitutionUser
    serializer_class = InstitutionUserSerializer
    filter_backends = [SearchFilter, DjangoFilterBackend, OrderingFilter]
    filterset_class = InstitutionUserFilter
    search_fields = ['username', 'first_name', 'last_name', 'email', 'uid']
    permission_classes = [
        permissions.GlobalAdminReadOnlyPermission |
        permissions.InstitutionAdminPermission |
        permissions.InstitutionLegalAdminReadOnlyPermission |
        permissions.InstitutionDataAdminReadOnlyPermission |
        permissions.InstitutionMemberReadOnlyPermission
    ]

    def get_queryset(self):
        queryset = self.filter_queryset_by_parents_lookups(InstitutionUser.objects)
        if not is_global_admin(self.request.user):
            inst_user = get_institution_user(self.request.user)
            if not inst_user.inst_admin and not inst_user.legal_admin and not inst_user.data_admin:
                queryset = queryset.filter(id=inst_user.id)
        return queryset.all().order_by('id')

    @action(detail=True, methods=['GET'],
            serializer_class=InstitutionCourseActivityExtendedSerializer,
            permission_classes=[permissions.GlobalAdminReadOnlyPermission |
                                permissions.InstitutionAdminReadOnlyPermission |
                                permissions.InstitutionLegalAdminReadOnlyPermission |
                                permissions.InstitutionDataAdminReadOnlyPermission |
                                permissions.InstitutionMemberReadOnlyPermission]
            )
    def activities(self, request, *args, **kwargs):
        """
            Manage learner informed consent
        """
        # Ensure permissions
        if not is_global_admin(self.request.user):
            inst_user = get_institution_user(self.request.user)
            if not inst_user.inst_admin and not inst_user.legal_admin and not inst_user.data_admin \
                    and int(kwargs['pk']) != inst_user.id:
                raise PermissionDenied('You cannot access this information')

        user = get_object_or_404(InstitutionUser, id=kwargs['pk'])
        qs = Activity.objects.filter(vle__institution_id=kwargs['parent_lookup_institution_id'], enabled=True).filter(
            Q(course__instructors__id=user.id) | Q(course__learners__id=user.id)
        ).distinct().filter(
            Q(start__isnull=True) | Q(start__lte=timezone.now()),
            Q(end__isnull=True) | Q(end__gte=timezone.now())
        )
        page = self.paginate_queryset(qs)
        if page is not None:
            data = self.serializer_class(page, many=True, context={'request': self.request}).data
            return self.get_paginated_response(data)

        data = self.serializer_class(qs, many=True, context={'request': self.request}).data
        return Response(self.get_paginated_response(data))

