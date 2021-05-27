#  Copyright (c) 2020 Roger Muñoz
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
""" Request model module."""

from django.db import models
from django.utils.translation import gettext_lazy as _

from .activity import Activity
from .assessment_session import AssessmentSession
from .base_model import BaseModel
from .instrument import Instrument
from .learner import Learner
from .message import Message

REQUEST_STATUS = (
    (0, _('Stored')),
    (1, _('Scheduled')),
    (2, _('Processing')),
    (3, _('Processed')),
    (4, _('Error')),
    (5, _('Timeout')),
    (6, _('Missing Provider'))
)


class Request(BaseModel):
    """ Request model. """
    learner = models.ForeignKey(Learner, null=False,
                                on_delete=models.CASCADE)

    status = models.IntegerField(choices=REQUEST_STATUS, null=False,
                                 default=0,
                                 help_text=_('Status for this request'))

    activity = models.ForeignKey(Activity, null=True, default=None,
                                 on_delete=models.CASCADE)

    instruments = models.ManyToManyField(Instrument)

    data = models.FileField(max_length=250, null=False, blank=False, help_text=_("Data path on storage."))

    session = models.ForeignKey(AssessmentSession, null=True, default=None, on_delete=models.CASCADE,
                                help_text=_("Assessment session for this request"))

    error_message = models.TextField(null=True,
                                     help_text=_("Error message when status is error"))

    message_code = models.ForeignKey(Message, null=True, default=None,
                                     on_delete=models.SET_NULL,
                                     help_text=_("Related message code"))

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __repr__(self):
        return "<Request(learner='%s', activity='%r', status='%r')>" % (self.learner, self.activity,
                                                                        self.status, )
