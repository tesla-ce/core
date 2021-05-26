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
""" Authentication urls module """
from django.urls import path

from .views import app_view
from .views import logout_view
from .views import token_refresh_view
from .views import token_view
from .views import user_data_view
from .views import user_view

app_name = 'tesla_ce.apps.api'
urlpatterns = [
    path('login', user_view),
    path('logout', logout_view),
    path('profile', user_data_view),
    path('approle', app_view),
    path('token', token_view),
    path('token/refresh', token_refresh_view),
]
