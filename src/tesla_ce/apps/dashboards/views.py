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
""" Test views module """
from base64 import urlsafe_b64decode
from base64 import urlsafe_b64encode

from django.conf import settings
from django.urls import reverse_lazy
from django.utils import timezone
from django.views.generic.edit import FormView
from rest_framework import viewsets
from rest_framework_extensions.mixins import NestedViewSetMixin

from tesla_ce.client import Client
from tesla_ce.client import ConfigManager
from tesla_ce.models import Alert
from tesla_ce.models import AssessmentSession
from tesla_ce.models import Request
from .forms import TestActivityForm
from .forms import TestInitializationForm
from .serializers import AlertSerializer
from .serializers import RequestSerializer
from .serializers import SessionSerializer

_api_client = None


def get_api_client():
    global _api_client
    if _api_client is None:
        if 'api' in settings.TESLA_CONFIG.modules:
            api_config = settings.TESLA_CONFIG.modules['api']['config']
            config = ConfigManager()
            config.load_vault(role_id=api_config['VAULT_ROLE_ID'], secret_id=api_config['VAULT_SECRET_ID'])
            _api_client = Client(config)
        else:
            pass

    return _api_client


def get_connector_url(vle, course, activity, learner, locale):

    # Get the client
    client = get_api_client()

    # Create a new session
    session = client.create_assessment_session(activity, learner, locale)

    return session.assessmentsessiondata.connector.url, session.id


class TestIndexView(FormView):
    form_class = TestInitializationForm
    template_name = 'test/index.html'
    success_url = reverse_lazy('test_activity')

    def post(self, request, *args, **kwargs):
        form_class = self.get_form_class()
        form = self.get_form(form_class)
        if form.is_valid():
            connector_url, session_id = get_connector_url(form.cleaned_data['vle'],
                                              form.cleaned_data['course'],
                                              form.cleaned_data['activity'],
                                              form.cleaned_data['learner'],
                                              form.cleaned_data['locale'])
            connector_url = urlsafe_b64encode(connector_url.encode('utf8')).decode()
            self.success_url += '?session_id={}&connector_url={}'.format(session_id, connector_url)
            return self.form_valid(form)
        else:
            return self.form_invalid(form)


class TestActivityView(FormView):
    form_class = TestActivityForm
    template_name = 'test/activity.html'
    success_url = reverse_lazy('test_index')

    def get_context_data(self, **kwargs):
        """Use this to add extra context."""
        context = super(TestActivityView, self).get_context_data(**kwargs)
        session_id = self.request.GET.get('session_id', None)
        connector_url = self.request.GET.get('connector_url', None)
        if connector_url is not None:
            context['session_id'] = session_id
            context['connector_url'] = urlsafe_b64decode(connector_url.encode('utf8')).decode()
        return context

    def post(self, request, *args, **kwargs):
        form_class = self.get_form_class()
        form = self.get_form(form_class)
        if form.is_valid():
            session = AssessmentSession.objects.get(id=int(form.data['session_id']))
            session.closed_at = timezone.now()
            session.save()
            return self.form_valid(form)
        else:
            return self.form_invalid(form)


class SessionView(viewsets.ReadOnlyModelViewSet):
    queryset = AssessmentSession.objects.all()
    serializer_class = SessionSerializer


class SessionAlertsView(NestedViewSetMixin, viewsets.ReadOnlyModelViewSet):
    queryset = Alert.objects
    serializer_class = AlertSerializer


class SessionRequestView(NestedViewSetMixin, viewsets.ReadOnlyModelViewSet):
    queryset = Request.objects
    serializer_class = RequestSerializer
