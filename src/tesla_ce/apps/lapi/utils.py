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


def is_authenticated(request, instituton_id, learner_id, data):

    if data['learner_id'] != str(learner_id):
        return False
    try:
        if settings.AUTHENTICATION_DISABLED and (
                settings.AUTHENTICATION_DISABLED_ROLES == "__all__" or
                "LEARNER" in settings.AUTHENTICATION_DISABLED_ROLES
        ):
            return True
        if not request.user.is_authenticated:
            return False
        if isinstance(request.user, AuthenticatedUser):
            return request.user.type == 'learner' and request.user.sub == str(learner_id)
        if request.user.learner.learner_id == learner_id and request.user.learner.institution_id == instituton_id:
            return True
        return False
    except request.user._meta.model.learner.RelatedObjectDoesNotExist:
        # Current user is not a learner
        return False
    return False
