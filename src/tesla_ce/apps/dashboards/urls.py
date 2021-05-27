# Copyright (c) 2020 Xavier Baró
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
""" Dashboards urls module """
from django.conf import settings
from django.conf.urls import url
from django.urls import include
from django.urls import path
from rest_framework_extensions.routers import ExtendedSimpleRouter

from .views import SessionAlertsView
from .views import SessionRequestView
from .views import SessionView
from .views import TestActivityView
from .views import TestIndexView

# Create the base router
router = ExtendedSimpleRouter()

# Session router
session_router = router.register(r'session', SessionView, basename='session')
session_alerts_router = session_router.register(r'alert',
                                                SessionAlertsView,
                                                basename='session-alert',
                                                parents_query_lookups=['session_id'])
session_request_router = session_router.register(r'request',
                                                 SessionRequestView,
                                                 basename='session-request',
                                                 parents_query_lookups=['session_id'])

# Add front end access
urlpatterns = [
    #url(r'^ui$', TemplateView.as_view(template_name="dashboards/index.html"), name="dashboards-home"),
]
# urlpatterns = format_suffix_patterns(urlpatterns)
if settings.DEBUG:
    urlpatterns += [
        url('test$', TestIndexView.as_view(), name='test_index'),
        url('test/activity$', TestActivityView.as_view(), name='test_activity'),
        path('', include(router.urls))
    ]
