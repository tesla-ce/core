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
""" Django URLs definition """
from django.conf import settings
from django.http import HttpResponse
from django.shortcuts import redirect
from django.templatetags.static import static
from django.urls import include
from django.urls import path
from django.urls import re_path

from tesla_ce import get_default_client


def favicon_view(request):
    """
        Allow the exportation of favicon when requested
        :param request: HTTP request
        :return: Redirects to the static URL with favicon
    """
    return redirect(static('img/favicon.ico'))


def version_view(request, module=None):
    """
        Return the version of the code
        :param request: HTTP request
        :param module: The module
        :return: Returns the version
    """
    version = get_default_client().version

    return HttpResponse('{"version": "' + version + '"}', content_type='application/json')


urlpatterns = [
    re_path(r'^favicon\.ico$', favicon_view),
    path('', include('django_prometheus.urls')),
    re_path(r'^(?P<module>\D+)/version/$', version_view),
]

if 'api' in settings.TESLA_MODULES:
    urlpatterns += [
        path('api/', include('tesla_ce.apps.api.urls')),
        path('api/webhooks/', include('tesla_ce.apps.webhooks.urls')),
    ]

if 'lapi' in settings.TESLA_MODULES:
    urlpatterns += [
        path('lapi/', include('tesla_ce.apps.lapi.urls'))
    ]
