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
""" Course views module """
import botocore
import json

from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.core.exceptions import ValidationError
from django.utils import timezone
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.filters import OrderingFilter
from rest_framework.filters import SearchFilter
from rest_framework.views import Response
from rest_framework.views import status
from rest_framework_extensions.mixins import NestedViewSetMixin

from tesla_ce import tasks

from tesla_ce.lib.exception import tesla_report_exception

from tesla_ce.apps.api import permissions
from tesla_ce.apps.api.v2.serializers import VLECourseActivityInstrumentSerializer
from tesla_ce.apps.api.v2.serializers import VLECourseActivitySerializer
from tesla_ce.apps.api.v2.serializers import VLECourseActivityAttachmentSerializer
from tesla_ce.models import Activity


# pylint: disable=too-many-ancestors
class VLECourseActivityViewSet(NestedViewSetMixin, viewsets.ModelViewSet):
    """
    API endpoint that allows activity in a course to be viewed or edited.
    """
    model = Activity
    serializer_class = VLECourseActivitySerializer
    permission_classes = [
        permissions.VLEPermission
    ]
    filter_backends = [SearchFilter, DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['vle_id', 'vle_activity_type', 'vle_activity_id', 'course_id', 'name']
    search_fields = ['vle_id', 'vle_activity_type', 'vle_activity_id', 'course_id', 'name']
    queryset = Activity.objects

    @action(detail=True, methods=['GET', 'POST',], url_path=r'attachment/(?P<learner_id>[\w|-]+)',
            serializer_class=VLECourseActivityAttachmentSerializer)
    def attachment(self, request, **kwargs):
        """
            Return the list of instruments (if any) waiting to process the attachment of the activity
        """
        activity = self.get_object()
        try:
            learner = activity.course.learners.get(learner_id=kwargs['learner_id'])
        except activity.course.learners.model.DoesNotExist:
            return Response("Learner does not exist", status=404)
        except ValidationError as verr:
            return Response(verr.__str__(), status=400)

        # For GET, just return the list of instruments waiting for the attachment
        if request.method == 'GET':
            activity_instruments = activity.get_learner_instruments(learner)

            # Filter instruments that accept attachments
            attachment_instruments = []
            for inst in activity_instruments:
                if inst.instrument_id in [4, 5]:
                    # Instruments that work with attachments (plag, fa)
                    attachment_instruments.append(inst)
                elif inst.instrument_id in [1, 3]:
                    # Instruments that can work with attachments (fr, vr)
                    options = inst.get_options()
                    if options is not None and 'offline' in options and options['offline']:
                        attachment_instruments.append(inst)
            return Response(VLECourseActivityInstrumentSerializer(instance=attachment_instruments, many=True).data)

        # POST action will store the attachment as a new request
        serializer = self.serializer_class(data=request.data, context={'request': request, 'view': self})
        try:
            if serializer.is_valid():
                # Get the filename
                metadata = serializer.data.get('metadata')
                if metadata is None:
                    filename = 'request'
                else:
                    filename = metadata.get('filename', 'document')
                # Generate the target path for the request
                path = '{}/requests/{}/{}/{}/documents/{}_{}'.format(
                    learner.institution_id,
                    learner.learner_id,
                    activity.course_id,
                    activity.id,
                    timezone.now().strftime("%Y%m%d_%H%M%S_%f"),
                    filename)

                # Add url parameters to data
                attachment_data = serializer.data
                attachment_data['learner_id'] = str(learner.learner_id)
                attachment_data['course_id'] = activity.course_id
                attachment_data['activity_id'] = activity.id

                # Remove extra data arguments
                if 'close_session' in attachment_data:
                    del attachment_data['close_session']
                if 'close_at' in attachment_data:
                    del attachment_data['close_at']

                # Store the request
                resp = default_storage.save(path, ContentFile(json.dumps(attachment_data).encode('utf-8')))

                # Notify the new stored request
                kwargs = {
                    'activity_id': activity.id,
                    'learner_id': str(learner.learner_id),
                    'path': path,
                    'instruments': serializer.data['instruments'],
                    'session_id': serializer.data.get('session_id')
                }
                tasks.requests.verification.create_request.apply_async(kwargs=kwargs)

                return Response({"status": "OK", "path": resp})

            return Response(status=status.HTTP_400_BAD_REQUEST,
                            data={"status": "ERROR", 'errors': serializer.errors},
                            content_type="application/json")
        except botocore.exceptions.ClientError as cli_err:
            tesla_report_exception(cli_err)
            return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            data={"status": "ERROR", 'errors': cli_err.response},
                            content_type="application/json")

        except Exception as ex:
            tesla_report_exception(ex)
            return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            data={"status": "ERROR", 'errors': ex},
                            content_type="application/json")
