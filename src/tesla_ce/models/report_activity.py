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

from .activity import Activity
from .base_model import BaseModel
from .learner import Learner

REPORT_ALERT_LEVEL = (
    (0, _('Pending')),
    (1, _('No Information')),
    (2, _('Ok')),
    (3, _('Warning')),
    (4, _('Alert')),
)


class ReportActivity(BaseModel):
    """ Report Activity model. """

    learner = models.ForeignKey(Learner, null=False, blank=False, on_delete=models.CASCADE,
                                help_text=_('Learner related to this report.'))

    activity = models.ForeignKey(Activity, null=False, blank=False, on_delete=models.CASCADE,
                                 help_text=_('Activity related to this report.'))

    identity_level = models.SmallIntegerField(choices=REPORT_ALERT_LEVEL, null=False, default=0,
                                              help_text=_('Alert level for learner identity.'))
    content_level = models.SmallIntegerField(choices=REPORT_ALERT_LEVEL, null=False, default=0,
                                             help_text=_('Alert level for content authorship.'))
    integrity_level = models.SmallIntegerField(choices=REPORT_ALERT_LEVEL, null=False, default=0,
                                               help_text=_('Alert level for system integrity.'))

    data = models.FileField(max_length=250, null=True, blank=False,
                            help_text=_("Path to the content of this report."))

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = (('activity', 'learner'),)

    def __repr__(self):
        return "<ReportActivity(id='%r', learner_id='%r' activity_id='%r')>" % (
            self.id, self.learner_id, self.activity_id)
