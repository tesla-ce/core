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
""" Provider Enrolment views module """
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import NotAcceptable
from rest_framework.exceptions import NotFound
from rest_framework.exceptions import PermissionDenied
from rest_framework.filters import OrderingFilter
from rest_framework.filters import SearchFilter
from rest_framework.views import Response
from rest_framework_extensions.mixins import NestedViewSetMixin

from tesla_ce.apps.api import permissions
from tesla_ce.apps.api.v2.serializers import ProviderEnrolmentSampleSerializer
from tesla_ce.apps.api.v2.serializers import ProviderEnrolmentSerializer
from tesla_ce.models import Enrolment
from tesla_ce.models import EnrolmentSample
from tesla_ce.models import EnrolmentSampleValidation
from tesla_ce.models import Provider


# pylint: disable=too-many-ancestors
class ProviderEnrolmentViewSet(NestedViewSetMixin, viewsets.ModelViewSet):
    """
    API endpoint that allows Provider access enrolment samples.
    """
    queryset = Enrolment.objects
    lookup_field = 'learner__learner_id'
    serializer_class = ProviderEnrolmentSerializer
    filter_backends = [SearchFilter, DjangoFilterBackend, OrderingFilter]
    permission_classes = [
        permissions.ProviderPermission
    ]
    '''
    filterset_fields = ['activity_type', 'external_token', 'description', 'conf', 'vle']
    search_fields = ['activity_type', 'external_token', 'description', 'conf', 'vle']
    '''

    @action(detail=True, methods=['POST', ], serializer_class=ProviderEnrolmentSampleSerializer)
    def unlock(self, request, *args, **kwargs):
        """
            Unlock a locked model
        """
        try:
            model = self.get_queryset().get(learner__learner_id=kwargs['learner__learner_id'])
        except Enrolment.DoesNotExist:
            raise NotFound('No model to unlock')

        if not model.is_locked:
            raise NotAcceptable('Model is not locked')
        token = self.request.data.get('token')
        if str(model.locked_by) != str(token):
            raise PermissionDenied('Invalid unlock token')
        model.locked_by = None
        model.locked_at = None
        model.save()

        return Response('Model unlocked')

    @action(detail=True, methods=['GET', ], serializer_class=ProviderEnrolmentSampleSerializer)
    def available_samples(self, request, *args, **kwargs):
        """
            Get available samples for this enrolment model
        """
        try:
            used_samples = list(self.get_queryset()
                                .get(learner__learner_id=kwargs['learner__learner_id'])
                                .model_samples.values_list('id', flat=True).all())
        except Enrolment.DoesNotExist:
            used_samples = []
        provider = Provider.objects.get(id=kwargs['parent_lookup_provider_id'])
        sample_ids = list(EnrolmentSampleValidation.objects.filter(
            sample__learner__learner_id=kwargs['learner__learner_id'],
            provider__instrument=provider.instrument,
            status=1).exclude(sample_id__in=used_samples).values_list('sample', flat=True).all())
        samples = EnrolmentSample.objects.filter(id__in=sample_ids, status=1)

        page = self.paginate_queryset(samples)
        if page is not None:
            data = self.serializer_class(page, many=True).data
            return self.get_paginated_response(data)

        data = self.serializer_class(samples, many=True).data
        return Response(self.get_paginated_response(data))

    @action(detail=True, methods=['GET', ], serializer_class=ProviderEnrolmentSampleSerializer)
    def used_samples(self, request, *args, **kwargs):
        """
            Get used samples for this enrolment model
        """
        try:
            used_samples = list(self.get_queryset()
                                .get(learner__learner_id=kwargs['learner__learner_id'])
                                .model_samples.values_list('id', flat=True).all())
        except Enrolment.DoesNotExist:
            used_samples = []
        samples = EnrolmentSample.objects.filter(id__in=used_samples)
        page = self.paginate_queryset(samples)
        if page is not None:
            data = self.serializer_class(page, many=True).data
            return self.get_paginated_response(data)

        data = self.serializer_class(samples, many=True).data
        return Response(self.get_paginated_response(data))
