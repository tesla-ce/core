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
""" Enrolment sample validation model module."""

from django.db import models
from django.utils.translation import gettext_lazy as _

from .base_model import BaseModel
from .enrolment_sample import EnrolmentSample
from .learner import get_learner_enrolment
from .message import Message
from .provider import Provider

VALIDATION_STATUS = (
    (0, _('Validating')),
    (1, _('Valid')),
    (2, _('Error')),
    (3, _('Timeout')),
    (4, _('Waiting External Service')),
)


class EnrolmentSampleValidation(BaseModel):
    """ Enrolment Sample Validation model. """
    sample = models.ForeignKey(EnrolmentSample, null=False, on_delete=models.CASCADE,
                               help_text=_("Related Sample"))

    provider = models.ForeignKey(Provider, null=False, on_delete=models.CASCADE,
                                 help_text=_("Provider that performed the validation of the sample"))

    status = models.IntegerField(choices=VALIDATION_STATUS, null=False,
                                 default=0,
                                 help_text=_('Validation status for this sample'))

    info = models.FileField(max_length=250, null=False, blank=False,
                            help_text=_("Validation information path on storage."))

    contribution = models.DecimalField(null=True, decimal_places=2, max_digits=5, default=None,
                                       help_text=_('Estimated contribution of this sample to the enrolment model'))

    error_message = models.TextField(null=True, blank=None, default=None,
                                     help_text=_("Error message when status is error"))

    message_code = models.ForeignKey(Message, null=True, default=None,
                                     on_delete=models.SET_NULL,
                                     help_text=_("Related message code"))

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = (('sample', 'provider'),)

    def __repr__(self):
        return "<EnrolmentSampleValidation(sample='%s', provider='%s', status='%r')>" % (
            self.sample_id, self.provider_id, self.get_status_display())

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        super().save(force_insert, force_update, using, update_fields)
        # Invalidate cached value
        get_learner_enrolment.invalidate(self.sample.learner_id)
