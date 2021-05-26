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
""" Enrolment sample request model module."""

from django.db import models
from django.utils.translation import gettext_lazy as _

from .base_model import BaseModel
from .instrument import Instrument
from .learner import Learner
from .message import Message

SAMPLE_STATUS = (
    (0, _('Stored')),
    (1, _('Valid')),
    (2, _('Error')),
    (3, _('Timeout')),
    (4, _('Missing Validator')),
)


class EnrolmentSample(BaseModel):
    """ Enrolment Sample Request model. """
    learner = models.ForeignKey(Learner, null=False,
                                on_delete=models.CASCADE,
                                help_text=_("Related learner"))

    status = models.IntegerField(choices=SAMPLE_STATUS, null=False,
                                 default=0,
                                 help_text=_('Status for this sample'))

    instruments = models.ManyToManyField(Instrument, help_text=_("Instruments this sample is collected for"))

    error_message = models.TextField(null=True, blank=None, default=None,
                                     help_text=_("Error message when status is error"))

    message_code = models.ForeignKey(Message, null=True, default=None,
                                     on_delete=models.SET_NULL,
                                     help_text=_("Related message code"))

    data = models.FileField(max_length=250, null=False, blank=False, help_text=_("Data path on storage."))

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __repr__(self):
        return "<EnrolmentSample(learner='%s', status='%r')>" % (self.learner, self.status, )
