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
""" Activity model module."""

from django.db import models
from django.utils.translation import gettext_lazy as _

from .base_model import BaseModel
from .course import Course
from .vle import VLE


class Activity(BaseModel):
    """ Activity model. """
    vle = models.ForeignKey(VLE, null=False, blank=False,
                            on_delete=models.CASCADE,
                            help_text=_('Activity VLE.'))

    course = models.ForeignKey(Course, null=False, blank=False,
                            on_delete=models.CASCADE,
                            help_text=_('Activity VLE.'))

    vle_activity_type = models.CharField(max_length=250, null=False, blank=False,
                                         help_text=_("Activity type on the VLE."))

    vle_activity_id = models.CharField(max_length=250, null=False, blank=False,
                                       help_text=_("Activity id on the VLE."))

    description = models.TextField(null=True, blank=True,
                                   help_text=_("Activity description."))

    name = models.CharField(max_length=255, null=True, blank=True,
                            help_text=_("Activity name."))

    enabled = models.BooleanField(null=None, blank=None, default=False,
                                  help_text=_("Whether this activity is enabled or not"))

    start = models.DateTimeField(blank=True, null=True,
                                 help_text=_("When activity starts"))

    end = models.DateTimeField(blank=True, null=True,
                               help_text=_("When activity ends"))

    conf = models.TextField(null=True, blank=True,
                            help_text=_("Activity conf."))

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = (('vle', 'vle_activity_type', 'vle_activity_id'),)

    def __repr__(self):
        return "<Activity(id='%r', course_id='%r' vle_id='%r', vle_act_type='%s', vle_act_id='%r', enabled='%r')>" % (
            self.id, self.course_id, self.course.vle_id, self.vle_activity_type, self.vle_activity_id, self.enabled)

    def get_learner_instruments(self, learner):
        """
        Get the list of instruments that should be activated for this activity for a given learner.

        :param learner: The learner identifier
        :type learner: uuid

        :return: List of instrument configurations for this activity
        """
        disabled_instruments = []
        if learner.send['is_send'] and 'disabled_instruments' in learner.send['send']:
            disabled_instruments = learner.send['send']['disabled_instruments']

        primary_instruments = self.configuration.filter(active=True,
                                                        alternative_to=None
                                                        ).exclude(instrument_id__in=disabled_instruments).all()
        excluded_instruments = self.configuration.filter(active=True,
                                                         alternative_to=None,
                                                         instrument_id__in=disabled_instruments).all()
        alternative_instruments = []
        for exc_inst in excluded_instruments:
            alternative = exc_inst.activityinstrument_set.filter(active=True).all()
            alternative_instruments += list(alternative)

        return list(primary_instruments) + alternative_instruments
