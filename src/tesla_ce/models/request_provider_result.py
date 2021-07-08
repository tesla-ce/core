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
""" Request Provider Result model module."""

from django.db import models
from django.db import transaction
from django.utils.translation import gettext_lazy as _

from .base_model import BaseModel
from .histogram_activity_instrument import HistogramActivityInstrument
from .histogram_activity_provider import HistogramActivityProvider
from .histogram_learner_instrument import HistogramLearnerInstrument
from .histogram_learner_provider import HistogramLearnerProvider
from .message import Message
from .provider import Provider
from .request import Request
from .request_result import RESULT_CODE
from .request_result import RESULT_STATUS


class RequestProviderResult(BaseModel):
    """ Request result for a provider. """

    request = models.ForeignKey(Request, null=False,
                                on_delete=models.CASCADE, help_text=_('Request related to this result'))

    provider = models.ForeignKey(Provider, null=False,
                                 on_delete=models.CASCADE, help_text=_('Provider related to this result'))

    status = models.IntegerField(choices=RESULT_STATUS, null=False,
                                 default=0,
                                 help_text=_('Status for this result'))

    result = models.FloatField(null=True, default=0.0,
                               help_text=_('Normalized result value'))

    error_message = models.TextField(null=True,
                                     help_text=_("Error message when status is error"))

    message_code = models.ForeignKey(Message, null=True, default=None,
                                     on_delete=models.SET_NULL,
                                     help_text=_("Related message code"))

    code = models.IntegerField(choices=RESULT_CODE, null=False, default=0,
                               help_text=_("Result code provided after performing the verification process"))

    audit = models.FileField(max_length=250, null=False, blank=False,
                             help_text=_("Audit data for this result."))

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = (('provider', 'request'),)

    def __repr__(self):
        return "<RequestProviderResult(request='%s', provider='%s', status='%r', " \
               "result='%r', code='%r')>" % (
                   self.request, self.provider.acronym, self.get_status_display(),
                   self.result, self.get_code_display()
        )

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        super().save(force_insert, force_update, using, update_fields)

        # Update histograms
        if self.status == 1:
            bin = 'b{}'.format(min(int(self.result * 10), 9))
            with transaction.atomic():
                try:
                    h1 = HistogramLearnerInstrument.objects.get(learner=self.request.learner,
                                                                instrument=self.provider.instrument)
                    setattr(h1, bin, getattr(h1, bin) + 1)
                    h1.save()
                except HistogramLearnerInstrument.DoesNotExist:
                    h1 = HistogramLearnerInstrument(learner=self.request.learner,
                                                    instrument=self.provider.instrument)
                    setattr(h1, bin, 1)
                    h1.save()
                try:
                    h2 = HistogramLearnerProvider.objects.get(learner=self.request.learner,
                                                              provider=self.provider)
                    setattr(h2, bin, getattr(h2, bin) + 1)
                    h2.save()
                except HistogramLearnerProvider.DoesNotExist:
                    h2 = HistogramLearnerProvider(learner=self.request.learner,
                                                  provider=self.provider)
                    setattr(h2, bin, 1)
                    h2.save()
                try:
                    h3 = HistogramActivityInstrument.objects.get(activity=self.request.activity,
                                                                 instrument=self.provider.instrument)
                    setattr(h3, bin, getattr(h3, bin) + 1)
                    h3.save()
                except HistogramActivityInstrument.DoesNotExist:
                    h3 = HistogramActivityInstrument(activity=self.request.activity,
                                                     instrument=self.provider.instrument)
                    setattr(h3, bin, 1)
                    h3.save()
                try:
                    h4 = HistogramActivityProvider.objects.get(activity=self.request.activity,
                                                               provider=self.provider)
                    setattr(h4, bin, getattr(h4, bin) + 1)
                    h4.save()
                except HistogramActivityProvider.DoesNotExist:
                    h4 = HistogramActivityProvider(activity=self.request.activity,
                                                   provider=self.provider)
                    setattr(h4, bin, 1)
                    h4.save()
