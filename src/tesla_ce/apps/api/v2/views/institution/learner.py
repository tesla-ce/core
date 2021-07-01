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
""" Institution Learner views module """
from django.utils import timezone

from django_filters.rest_framework import DjangoFilterBackend

from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.filters import OrderingFilter
from rest_framework.filters import SearchFilter
from rest_framework.views import Response
from rest_framework.views import status
from rest_framework.exceptions import PermissionDenied
from rest_framework_extensions.mixins import DetailSerializerMixin
from rest_framework_extensions.mixins import NestedViewSetMixin

from tesla_ce.apps.api import permissions
from tesla_ce.apps.api.v2.serializers import InstitutionLearnerDetailSerializer
from tesla_ce.apps.api.v2.serializers import InstitutionLearnerSerializer
from tesla_ce.apps.api.v2.serializers import InstitutionLearnerICBodySerializer

from tesla_ce.models import InformedConsent
from tesla_ce.models import Learner
from tesla_ce.models.user import get_institution_user
from tesla_ce.models.user import is_global_admin


def is_newer_versions(current, new):
    """
        Compare if a version is newer than the current one
        :param current: Current version in standard format x.y.z
        :type current: str
        :param new: New version in standard format x.y.z
        :type new: str
        :return: True if the new version is newer than the current. False otherwise.
    """
    current_version = [int(ver_part) for ver_part in current.split('.')]
    new_version = [int(ver_part) for ver_part in new.split('.')]
    if new_version[0] > current_version[0] or\
            (new_version[0] == current_version[0] and
            (
                    new_version[1] > current_version[1] or
                    (new_version[1] == current_version[1] and new_version[2] > current_version[2])
            )):
        return True
    return False


# pylint: disable=too-many-ancestors
class InstitutionLearnerViewSet(NestedViewSetMixin, DetailSerializerMixin, viewsets.ModelViewSet):
    """
    API endpoint that allows learners to be viewed or edited.
    """
    model = Learner
    serializer_class = InstitutionLearnerSerializer
    serializer_detail_class = InstitutionLearnerDetailSerializer
    permission_classes = [
        permissions.GlobalAdminReadOnlyPermission |
        permissions.InstitutionAdminPermission |
        permissions.InstitutionLegalAdminReadOnlyPermission |
        permissions.InstitutionDataAdminReadOnlyPermission |
        permissions.InstitutionLearnerReadOnlyPermission
    ]
    filter_backends = [SearchFilter, DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['uid', 'email', 'first_name', 'last_name']
    search_fields = ['uid', 'email', 'first_name', 'last_name']

    def get_queryset(self):
        queryset = self.filter_queryset_by_parents_lookups(Learner.objects)
        if not is_global_admin(self.request.user):
            inst_user = get_institution_user(self.request.user)
            if not inst_user.inst_admin and not inst_user.legal_admin and not inst_user.data_admin:
                queryset = queryset.filter(id=inst_user.id)
        return queryset.all().order_by('id')

    @action(detail=True, methods=['POST', 'DELETE'], permission_classes=[permissions.InstitutionLearnerPermission])
    def ic(self, request, *args, **kwargs):
        """
            Manage learner informed consent
        """
        learner = Learner.objects.get(
            pk=kwargs['pk'],
            institution_id=kwargs['parent_lookup_institution_id']
        )

        if learner.id != request.user.id:
            raise PermissionDenied('Only learner can manage his/her IC')

        if request.method == 'POST':
            # Accept informed consent
            serializer = InstitutionLearnerICBodySerializer(data=request.data)
            if serializer.is_valid():
                try:
                    consent = InformedConsent.objects.get(institution=learner.institution,
                                                          version=serializer.validated_data['version'])
                    if learner.consent is not None and \
                            learner.consent_rejected is None and \
                            not is_newer_versions(learner.consent.version, consent.version):
                        return Response('Cannot downgrade consent', status=status.HTTP_400_BAD_REQUEST)

                except InformedConsent.DoesNotExist:
                    return Response('Informed Consent not found', status=status.HTTP_404_NOT_FOUND)

                # Update the informed consent of the learner
                learner.consent = consent
                learner.consent_accepted = timezone.now()
                learner.consent_rejected = None
                learner.save()
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        elif request.method == 'DELETE':
            # Reject the current informed consent for this learner
            if learner.consent is not None and learner.consent_rejected is None:
                learner.consent_rejected = timezone.now()
                learner.save()
            else:
                return Response('No Informed Consent to reject', status=status.HTTP_404_NOT_FOUND)

        serializer = self.get_serializer(learner)
        return Response(serializer.data)

    @action(detail=True, methods=['GET'])
    def enrolment(self, request, *args, **kwargs):
        """
            Get learner enrolment status
        """
        learner = Learner.objects.get(
            pk=kwargs['pk'],
            institution_id=kwargs['parent_lookup_institution_id']
        )

        if 'activity_id' in request.query_params:
            return Response(learner.missing_enrolments(int(request.query_params['activity_id'])))

        return Response(learner.enrolment_status)
