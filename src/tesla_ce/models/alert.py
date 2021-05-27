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
""" Alert message model module."""

from django.db import models
from django.utils.translation import gettext_lazy as _

from .activity import Activity
from .assessment_session import AssessmentSession
from .base_model import BaseModel
from .instrument import Instrument
from .learner import Learner
from .message import Message

ALERT_LEVEL = (
    (0, _('Info')),
    (1, _('Warning')),
    (2, _('Alert')),
    (3, _('Error')),
)


def get_alert_from_value(value):
    """
        Get the alert level integer value from an string
        :param value: String with the alert level
        :type value: str
        :return: Alert level ID
        :rtype: int
    """
    if value.upper() == 'INFO':
        return 0
    if value.upper() == 'WARNING':
        return 1
    if value.upper() == 'ALERT':
        return 2
    if value.upper() == 'ERROR':
        return 3
    return None


class Alert(BaseModel):
    """ Alert message model. """
    learner = models.ForeignKey(Learner, null=False,
                                on_delete=models.CASCADE,
                                help_text=_("Related learner"))

    level = models.IntegerField(choices=ALERT_LEVEL, null=False,
                                default=0,
                                help_text=_('Level of the alert'))

    instruments = models.ManyToManyField(Instrument, help_text=_("Instruments related to this alert"))

    session = models.ForeignKey(AssessmentSession, null=True, default=None,
                                on_delete=models.SET_NULL,
                                help_text=_("Related assessment session"))

    activity = models.ForeignKey(Activity, null=False,
                                 on_delete=models.CASCADE,
                                 help_text=_("Related activity"))

    message_code = models.ForeignKey(Message, null=True, default=None,
                                     on_delete=models.SET_NULL,
                                     help_text=_("Related message code"))

    data = models.FileField(max_length=250, null=False, blank=False, help_text=_("Data path on storage."))
    raised_at = models.DateTimeField(null=False, help_text=_('When the alert was raised.'))

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __repr__(self):
        return "<Alert(learner='%s', activity='%r', level='%r')>" % (
            self.learner, self.activity, self.get_level_display()
        )
