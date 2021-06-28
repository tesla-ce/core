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
""" Learner API urls module """
from django.urls import path

from . import views

urlpatterns = [
    # Enrolment entries
    path(r'v1/enrolment/<int:institution_id>/<uuid:learner_id>/', views.LearnerEnrolment.as_view()),

    # Verification entries
    path(r'v1/verification/<int:institution_id>/<uuid:learner_id>/', views.LearnerVerification.as_view()),

    # Status entries
    path(r'v1/status/<int:institution_id>/<uuid:learner_id>/', views.StatusView.as_view()),

    # Alert messages
    path(r'v1/alert/<int:institution_id>/<uuid:learner_id>/', views.LearnerAlert.as_view()),

    # Profile
    path(r'v1/profile/<int:institution_id>/<uuid:learner_id>/', views.ProfileView.as_view()),
]
