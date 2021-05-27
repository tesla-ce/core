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
""" Histogram of learner results for a provider model module."""

from django.db import models
from django.utils.translation import gettext_lazy as _

from .base_model import BaseModel
from .learner import Learner
from .provider import Provider


class HistogramLearnerProvider(BaseModel):
    """ Histogram for provider results for a Learner model. """

    learner = models.ForeignKey(Learner, null=False, blank=False, on_delete=models.CASCADE,
                                help_text=_('Related Learner.'))

    provider = models.ForeignKey(Provider, null=False, blank=False, on_delete=models.CASCADE,
                                 help_text=_('Related Provider.'))

    b0 = models.BigIntegerField(null=False, default=0, help_text=_('Bin containing values from 0 to 9%'))
    b1 = models.BigIntegerField(null=False, default=0, help_text=_('Bin containing values from 10% to 19%'))
    b2 = models.BigIntegerField(null=False, default=0, help_text=_('Bin containing values from 20% to 29%'))
    b3 = models.BigIntegerField(null=False, default=0, help_text=_('Bin containing values from 30% to 39%'))
    b4 = models.BigIntegerField(null=False, default=0, help_text=_('Bin containing values from 40% to 49%'))
    b5 = models.BigIntegerField(null=False, default=0, help_text=_('Bin containing values from 50% to 59%'))
    b6 = models.BigIntegerField(null=False, default=0, help_text=_('Bin containing values from 60% to 69%'))
    b7 = models.BigIntegerField(null=False, default=0, help_text=_('Bin containing values from 70% to 79%'))
    b8 = models.BigIntegerField(null=False, default=0, help_text=_('Bin containing values from 80% to 89%'))
    b9 = models.BigIntegerField(null=False, default=0, help_text=_('Bin containing values from 90% to 100%'))

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = (('learner', 'provider'),)

    def __repr__(self):
        return "<HistogramLearnerProvider(id='%r', learner_id='%r', provider_id='%r')>" % (
            self.id, self.learner_id, self.provider_id)
