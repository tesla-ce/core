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
""" Report Activity Instrument model module."""

from django.db import models
from django.utils.translation import gettext_lazy as _

from .base_model import BaseModel
from .instrument import Instrument
from .report_activity import REPORT_ALERT_LEVEL
from .report_activity import ReportActivity


class ReportActivityInstrument(BaseModel):
    """ Report Activity model. """

    report = models.ForeignKey(ReportActivity, null=False, blank=False, on_delete=models.CASCADE,
                               help_text=_('Related Activity Report.'))

    instrument = models.ForeignKey(Instrument, null=False, blank=False, on_delete=models.CASCADE,
                                   help_text=_('Instrument related to this report detail.'))

    enrolment = models.SmallIntegerField(null=None, help_text=_('Enrolment percentage'))
    confidence = models.SmallIntegerField(null=None, help_text=_('Confidence percentage'))
    result = models.SmallIntegerField(null=None, help_text=_('Result percentage'))

    identity_level = models.SmallIntegerField(choices=REPORT_ALERT_LEVEL, null=False, default=0,
                                              help_text=_('Alert level for learner identity.'))
    content_level = models.SmallIntegerField(choices=REPORT_ALERT_LEVEL, null=False, default=0,
                                             help_text=_('Alert level for content authorship.'))
    integrity_level = models.SmallIntegerField(choices=REPORT_ALERT_LEVEL, null=False, default=0,
                                               help_text=_('Alert level for system integrity.'))

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = (('report', 'instrument'),)

    def __repr__(self):
        return "<ReportActivityInstrument(id='%r', report_id='%r' instrument_id='%r')>" % (
            self.id, self.report_id, self.instrument_id)
