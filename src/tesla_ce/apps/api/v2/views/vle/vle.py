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
""" VLE views module """
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.filters import OrderingFilter
from rest_framework.filters import SearchFilter
from rest_framework.views import Response
from rest_framework.views import status
from rest_framework_extensions.mixins import NestedViewSetMixin

from tesla_ce import get_default_client
from tesla_ce.apps.api import status as tesla_status
from tesla_ce.apps.api import permissions
from tesla_ce.apps.api.v2.serializers import VLELauncherBodySerializer
from tesla_ce.apps.api.v2.serializers import VLELauncherDataSerializer
from tesla_ce.apps.api.v2.serializers import VLENewAssessmentSessionBodySerializer
from tesla_ce.apps.api.v2.serializers import VLENewAssessmentSessionSerializer
from tesla_ce.apps.api.v2.serializers import VLESerializer
from tesla_ce.lib.exception import TeslaInvalidICException
from tesla_ce.lib.exception import TeslaMissingEnrolmentException
from tesla_ce.lib.exception import TeslaMissingICException
from tesla_ce.models import Activity
from tesla_ce.models import AssessmentSession
from tesla_ce.models import InstitutionUser
from tesla_ce.models import Learner
from tesla_ce.models import VLE


# pylint: disable=too-many-ancestors
class VLEViewSet(NestedViewSetMixin, viewsets.ReadOnlyModelViewSet):
    """
    API endpoint that allows access to VLE related models.
    """
    queryset = VLE.objects.all().order_by('created_at')
    serializer_class = VLESerializer
    permission_classes = [
        permissions.VLEPermission
    ]
    filter_backends = [SearchFilter, DjangoFilterBackend, OrderingFilter]
    '''
    filterset_fields = ['activity_type', 'external_token', 'description', 'conf', 'vle']
    search_fields = ['activity_type', 'external_token', 'description', 'conf', 'vle']
    '''

    @action(detail=True, methods=['POST',],
            serializer_class=VLENewAssessmentSessionSerializer)
    def assessment(self, request, pk):
        """
            Create a new assessment session
        """
        serializer = VLENewAssessmentSessionBodySerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        try:
            if serializer.data['session_id'] is not None:
                assessment_session = AssessmentSession.objects.get(id=serializer.data['session_id'])

                # Close the session
                if serializer.data['close'] is not None and serializer.data['close']:
                    if not assessment_session.is_active:
                        raise ValidationError('Cannot close a closed session')
                    assessment_session.close(auto=False, close_related=True)
                elif not assessment_session.is_active:
                    raise ValidationError('Closed session')

                resp = self.serializer_class(assessment_session)
                return Response(resp.data)
            vle = VLE.objects.get(pk=pk)
            activity = Activity.objects.get(vle=vle, vle_activity_type=serializer.data['vle_activity_type'],
                                            vle_activity_id=serializer.data['vle_activity_id'])
            learner = Learner.objects.get(institution=vle.institution, uid=serializer.data['vle_learner_uid'])

        except VLE.DoesNotExist:
            return Response("VLE not found", status=status.HTTP_404_NOT_FOUND)
        except Activity.DoesNotExist:
            return Response("Activity not found", status=status.HTTP_404_NOT_FOUND)
        except Learner.DoesNotExist:
            return Response("Learner not found", status=status.HTTP_404_NOT_FOUND)
        except AssessmentSession.DoesNotExist:
            return Response("Session not found", status=status.HTTP_404_NOT_FOUND)

        # Create the assessment session
        try:
            assessment_session = get_default_client(
            ).create_assessment_session(activity=activity,
                                        learner=learner,
                                        locale=serializer.data['locale'],
                                        max_ttl=serializer.data['max_ttl'],
                                        redirect_reject_url=serializer.data['redirect_reject_url'],
                                        reject_message=serializer.data['reject_message'],
                                        options=serializer.data['options']
                                        )
        except TeslaMissingICException:
            return Response({
                'status': tesla_status.TESLA_MISSING_IC,
                'message': 'Missing Informed Consent'
            }, status=status.HTTP_406_NOT_ACCEPTABLE)
        except TeslaInvalidICException:
            return Response({
                'status': tesla_status.TESLA_INVALID_IC,
                'message': 'Invalid Informed Consent'
            }, status=status.HTTP_406_NOT_ACCEPTABLE)
        except TeslaMissingEnrolmentException as exc:
            return Response({
                'status': tesla_status.TESLA_MISSING_ENROLMENT,
                'message': 'Missing Enrolment',
                'enrolments': exc.args[0]
            }, status=status.HTTP_406_NOT_ACCEPTABLE)

        resp = self.serializer_class(assessment_session)
        return Response(resp.data)

    @action(detail=True, methods=['POST', ],
            serializer_class=VLELauncherDataSerializer)
    def launcher(self, request, pk):
        """
            Create a new launcher url for VLE user
        """
        serializer = VLELauncherBodySerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        try:
            vle = VLE.objects.get(pk=pk)
            user = InstitutionUser.objects.get(institution=vle.institution, uid=serializer.data['vle_user_uid'])
            session = None
            if serializer.data['session_id'] is not None:
                session = AssessmentSession.objects.get(id=serializer.data['session_id'])
        except VLE.DoesNotExist:
            return Response("VLE not found", status=status.HTTP_404_NOT_FOUND)
        except InstitutionUser.DoesNotExist:
            return Response("User not found", status=status.HTTP_404_NOT_FOUND)
        except AssessmentSession.DoesNotExist:
            return Response("Session not found", status=status.HTTP_404_NOT_FOUND)

        # Create the launcher
        launcher = get_default_client().get_launcher_token(target=serializer.data['target'],
                                                           user=user,
                                                           target_url=serializer.data['target_url'],
                                                           session=session,
                                                           ttl=serializer.data['ttl'])
        resp = self.serializer_class(launcher)
        return Response(resp.data)
