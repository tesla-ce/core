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
""" Assessment session model module."""
from django.db import models
from django.utils.translation import gettext_lazy as _

from .activity import Activity
from .base_model import BaseModel
from .learner import Learner


class AssessmentSession(BaseModel):
    """ Assessment session model. """
    activity = models.ForeignKey(Activity, null=False,
                                 on_delete=models.CASCADE, help_text=_('Activity of this session'))

    learner = models.ForeignKey(Learner, null=False,
                                on_delete=models.CASCADE, help_text=_('Learner of this session'))

    started_at = models.DateTimeField(auto_now_add=True,
                                      help_text=_('Date when this assessment session started'))
    checked_at = models.DateTimeField(null=True, blank=True,
                                      help_text=_('Last time this assessment session has been checked'))
    closed_at = models.DateTimeField(null=True, blank=True,
                                     help_text=_('Date the assessment session has been closed'))

    @property
    def is_active(self):
        """
            Whether this assessment session is active or not

            :return: True if it is active or False if it is closed
            :rtype: bool
        """
        return self.closed_at is None

    def __repr__(self):
        return "<AssessmentSession(activity_id='%r',learner_id='%r', is_active='%r')>" % (
            self.activity_id, self.learner_id, self.is_active)
