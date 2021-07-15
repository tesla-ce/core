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
""" Report Activity model module."""

from django.db import models
from django.utils.translation import gettext_lazy as _

from .assessment_session import AssessmentSession
from .base_model import BaseModel
from .report_activity import ReportActivity
from .report_activity import REPORT_ALERT_LEVEL


class ReportActivitySession(BaseModel):
    """ Report for an Activity Assessment Session model. """

    report = models.ForeignKey(ReportActivity, null=False, blank=False, on_delete=models.CASCADE,
                               help_text=_('Related Activity Report.'))

    session = models.ForeignKey(AssessmentSession, null=False, blank=False, on_delete=models.CASCADE, unique=True,
                                help_text=_('Assessment Session related to this report.'))

    identity_level = models.SmallIntegerField(choices=REPORT_ALERT_LEVEL, null=False, default=0,
                                              help_text=_('Alert level for learner identity.'))
    content_level = models.SmallIntegerField(choices=REPORT_ALERT_LEVEL, null=False, default=0,
                                             help_text=_('Alert level for content authorship.'))
    integrity_level = models.SmallIntegerField(choices=REPORT_ALERT_LEVEL, null=False, default=0,
                                               help_text=_('Alert level for system integrity.'))

    total_requests = models.IntegerField(null=False, default=0,
                                         help_text=_('Number of requests on this session.'))
    pending_requests = models.IntegerField(null=False, default=0,
                                           help_text=_('Number of pending requests on this session.'))
    valid_requests = models.IntegerField(null=False, default=0,
                                         help_text=_('Number of valid requests on this session.'))
    processed_requests = models.IntegerField(null=False, default=0,
                                             help_text=_('Number of processed requests on this session.'))

    data = models.FileField(max_length=250, null=True, blank=False, default=None,
                            help_text=_("Path to the content of this report."))

    closed_at = models.DateTimeField(null=True, default=None, help_text=_('When the session report was closed'))

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __repr__(self):
        return "<ReportActivitySession(id='%r', session_id='%r', learner_id='%r' activity_id='%r')>" % (
            self.id, self.session.id, self.session.learner.learner_id, self.session.activity_id)
