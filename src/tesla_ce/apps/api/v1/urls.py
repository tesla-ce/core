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
""" Api v1 urls module """
from django.urls import path
from rest_framework.urlpatterns import format_suffix_patterns

from . import views

app_name = 'tesla_ce.apps.api'
urlpatterns = [
    # TIP URLs
    path(r'tip/users/id', views.tip.LearnerId.as_view()),
    path(r'tip/users/multiple/id', views.tip.MultipleLearnerId.as_view()),
    # TEP URLs
    path(r'tep/learner/<uuid:learner_id>/enrolment',
         views.tep.LearnerEnrolmentView.as_view()),
    path(r'tep/learner/<uuid:learner_id>/token',
         views.tep.LearnerEnrolmentTokenView.as_view()),
]

urlpatterns = format_suffix_patterns(urlpatterns)
