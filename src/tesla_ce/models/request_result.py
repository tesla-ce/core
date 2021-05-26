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

from .base_model import BaseModel
from .instrument import Instrument
from .message import Message
from .request import Request

RESULT_STATUS = (
    (0, _('Pending')),
    (1, _('Processed')),
    (2, _('Error')),
    (3, _('Timeout')),
    (4, _('Missing Provider')),
    (5, _('Missing Enrolment')),
    (6, _('Processing')),
    (7, _('Waiting External Service')),
)

RESULT_CODE = (
    (0, _('Pending')),
    (1, _('Ok')),
    (2, _('Warning')),
    (3, _('Alert'))
)


class RequestResult(BaseModel):
    """ Request result. """

    request = models.ForeignKey(Request, null=False,
                                on_delete=models.CASCADE, help_text=_('Request related to this result'))

    instrument = models.ForeignKey(Instrument, null=False,
                                   on_delete=models.CASCADE, help_text=_('Instrument related to this result'))

    status = models.IntegerField(choices=RESULT_STATUS, null=False,
                                 default=0,
                                 help_text=_('Status for this result'))

    result = models.FloatField(null=True, default=0.0,
                               help_text=_('Normalized result value, summarizing results from providers'))

    error_message = models.TextField(null=True,
                                     help_text=_("Error message when status is error"))

    message_code = models.ForeignKey(Message, null=True, default=None,
                                     on_delete=models.SET_NULL,
                                     help_text=_("Related message code"))

    code = models.IntegerField(choices=RESULT_CODE, null=False, default=0,
                               help_text=_("Result code provided after performing the verification process"))

    audit = models.FileField(max_length=250, null=False, blank=False,
                             help_text=_("Audit data for this request."))

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __repr__(self):
        return "<RequestResult(request='%s', instrument='%s', status='%r', " \
               "result='%r', code='%s')>" % (
                   self.request.id, self.instrument.acronym, self.get_status_display(),
                   self.result, self.get_code_display()
        )
