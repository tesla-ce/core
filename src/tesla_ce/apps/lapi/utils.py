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
from django.conf import settings

from tesla_ce.models import AuthenticatedUser
from tesla_ce.models import AuthenticatedModule
from tesla_ce.models import Learner
from tesla_ce.models import InstitutionUser


def is_authenticated(request, institution_id, learner_id, data):

    if data['learner_id'] != str(learner_id):
        return False
    try:
        if not request.user.is_authenticated:
            return False
        if isinstance(request.user, AuthenticatedUser):
            if request.user.type == 'learner' and request.user.sub == str(learner_id):
                return True
            return request.user.type == 'user' and request.path in request.user.allowed_scopes
        if isinstance(request.user, Learner):
            return str(request.user.learner_id) == str(learner_id) and request.user.institution_id == institution_id
        if isinstance(request.user, InstitutionUser):
            return str(request.user.learner.learner_id) == str(learner_id) and \
                   request.user.learner.institution_id == institution_id
        if isinstance(request.user, AuthenticatedModule) and request.user.type == 'vle':
            return request.user.module.institution_id == institution_id

    except request.user._meta.model.learner.RelatedObjectDoesNotExist:
        # Current user is not a learner
        return False
    return False
