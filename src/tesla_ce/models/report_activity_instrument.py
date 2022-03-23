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
from enum import Enum
import json

from django.core.files.base import ContentFile
from django.core.serializers.json import DjangoJSONEncoder
from django.db import models
from django.utils.translation import gettext_lazy as _

from .base_model import BaseModel
from .instrument import Instrument
from .report_activity import REPORT_ALERT_LEVEL
from .report_activity import ReportActivity
from .request_provider_result import RequestProviderResult
from .enrolment import Enrolment


class ResultFacts(Enum):
    """ Facts extracted from results """
    POSITIVE_LEARNER_RESULT_ABOVE_THRESHOLD = 1
    POSITIVE_LEARNER_RESULT_GOOD_INSTRUMENT = 2
    POSITIVE_LEARNER_RESULT_GOOD_ACTIVITY = 3
    POSITIVE_LEARNER_RESULT_FREQUENT = 4
    POSITIVE_CONFIDENCE_HIGH = 5
    NEUTRAL_MISSING_INFORMATION = 0
    NEGATIVE_LEARNER_RESULT_BELOW_THRESHOLD = -1
    NEGATIVE_LEARNER_RESULT_BAD_INSTRUMENT = -2
    NEGATIVE_LEARNER_RESULT_BAD_ACTIVITY = -3
    NEGATIVE_LEARNER_RESULT_NOT_FREQUENT = -4
    NEGATIVE_CONFIDENCE_LOW = -5


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

    audit_data = models.FileField(max_length=250, null=True, blank=False,
                                  help_text=_("Path to the audit data."))

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = (('report', 'instrument'),)

    def __repr__(self):
        return "<ReportActivityInstrument(id='%r', report_id='%r' instrument_id='%r')>" % (
            self.id, self.report_id, self.instrument_id)

    def get_activity_histogram(self):
        """
            Get the activity histogram
            :return: Histogram
        """
        return list(self.instrument.histogramactivityinstrument_set.values_list(
            'b0', 'b1', 'b2', 'b3', 'b4', 'b5', 'b6', 'b7', 'b8', 'b9').first())

    def get_learner_histogram(self):
        """
            Get the learner histogram
            :return: Histogram
        """
        return list(self.report.learner.histogramlearnerinstrument_set.filter(
            instrument=self.instrument
        ).values_list('b0', 'b1', 'b2', 'b3', 'b4', 'b5', 'b6', 'b7', 'b8', 'b9').first())

    def get_instrument_polarity(self):
        """
            Return the instrument polarity
            :return: 1 for normal polarity and -1 if inverted polarity
        """
        return 2 * int(not self.instrument.provider_set.first().inverted_polarity) - 1

    def get_result_bean(self):
        """
            Get the histogram bin where current result is included
            :return: Bin number
        """
        return min(int(self.result/10), 9)

    def get_thresholds(self):
        """
            Get the reference thresholds for current instrument
            :return: Reference thresholds
        """
        prov_thr = self.instrument.provider_set.first()
        return {
            "warning_below": prov_thr.warning_below,
            "alert_below": prov_thr.alert_below
        }

    def get_prob_learner(self):
        """
            Compute the probability to have current value for the learner
            :return: Probability value
        """
        hist_bin = self.get_result_bean()
        hist = self.get_learner_histogram()
        acc = hist[hist_bin]
        if hist_bin > 0:
            acc += hist[hist_bin - 1] / 2.0
        if hist_bin < 9:
            acc += hist[hist_bin + 1] / 2.0

        return acc / sum(hist)

    def get_prob_context(self):
        """
            Compute the probability to have current value in the context
            :return: Probability value
        """
        hist_bin = self.get_result_bean()
        hist = self.get_activity_histogram()
        acc = hist[hist_bin]
        if hist_bin > 0:
            acc += hist[hist_bin - 1] / 2.0
        if hist_bin < 9:
            acc += hist[hist_bin + 1] / 2.0

        return acc / sum(hist)

    def get_h_prob_learner(self):
        """
            Compute the probability to have better value for the learner
            :return: Probability value
        """
        hist_bin = self.get_result_bean()
        hist = self.get_learner_histogram()
        if self.get_instrument_polarity() > 0:
            acc = sum(hist[hist_bin + 1: 10])
        else:
            acc = sum(hist[0:hist_bin])

        return acc / sum(hist)

    def get_h_prob_context(self):
        """
            Compute the probability to have better value in the context
            :return: Probability value
        """
        hist_bin = self.get_result_bean()
        hist = self.get_activity_histogram()
        if self.get_instrument_polarity() > 0:
            acc = sum(hist[hist_bin + 1: 10])
        else:
            acc = sum(hist[0:hist_bin])

        return acc / sum(hist)

    def get_facts(self):
        """
            Get facts from results
            :return: Dictionary with facts
        """
        if self.confidence < 0.0001 or self.result is None:
            # Not enough information
            facts = {
                'neutral': [ResultFacts.NEUTRAL_MISSING_INFORMATION.name]
            }
        else:
            facts = {
                'positive': [],
                'negative': []
            }
            # Check confidence
            if self.confidence < 0.75:
                facts['negative'].append(ResultFacts.NEGATIVE_CONFIDENCE_LOW.name)
            else:
                facts['positive'].append(ResultFacts.POSITIVE_CONFIDENCE_HIGH.name)
            # Check thresholds
            thresholds = self.get_thresholds()
            inst_polarity = self.get_instrument_polarity()
            polarized_result = self.result * inst_polarity
            if thresholds["warning_below"] is not None and \
                    polarized_result >= thresholds["warning_below"] * inst_polarity:
                facts['positive'].append(ResultFacts.POSITIVE_LEARNER_RESULT_ABOVE_THRESHOLD.name)
            elif thresholds["alert_below"] is not None and \
                    polarized_result < thresholds["alert_below"] * inst_polarity:
                facts['negative'].append(ResultFacts.NEGATIVE_LEARNER_RESULT_BELOW_THRESHOLD.name)
            # Check probabilities
            h_prob_inst = self.get_h_prob_learner()
            if h_prob_inst < 0.4:
                facts['positive'].append(ResultFacts.POSITIVE_LEARNER_RESULT_GOOD_INSTRUMENT.name)
            elif h_prob_inst > 0.75:
                facts['negative'].append(ResultFacts.NEGATIVE_LEARNER_RESULT_BAD_INSTRUMENT.name)
            h_prob_act = self.get_h_prob_context()
            if h_prob_act < 0.4:
                facts['positive'].append(ResultFacts.POSITIVE_LEARNER_RESULT_GOOD_ACTIVITY.name)
            elif h_prob_act > 0.5:
                facts['negative'].append(ResultFacts.NEGATIVE_LEARNER_RESULT_BAD_ACTIVITY.name)
            if self.get_prob_learner() > 0.8:
                facts['positive'].append(ResultFacts.POSITIVE_LEARNER_RESULT_FREQUENT.name)

        return facts

    def update_audit(self):
        """
            Update the audit data for this report
        """
        if self.instrument.id == 1:
            # Build audit data for Face Recognition
            audit = self._build_fr_audit()
        else:
            # Other instruments will have no audit data
            audit = None

        audit_path = '{}/results/{}/{}/{}/report_audit_{}.json'.format(
            self.report.activity.vle.institution_id,
            self.report.learner.learner_id,
            self.report.activity.course.id,
            self.report.activity.id,
            self.instrument.acronym
        )

        if audit is not None:
            # Save the audit data
            self.audit_data.save(audit_path,
                                 ContentFile(json.dumps(audit, cls=DjangoJSONEncoder).encode('utf-8')))
        else:
            self.audit_data = None

        self.save()

    def _build_fr_audit(self):
        """
            Build audit data for Face Recognition instrument
            :return: Audit data object
        """
        provider_results = RequestProviderResult.objects.filter(provider__instrument=self.instrument,
                                                                request__learner=self.report.learner,
                                                                request__activity=self.report.activity
                                                                ).all().order_by('request__created_at', 'provider_id')
        audit = {
            'providers': {},
            'requests': {},
            'enrolment_samples': {},
        }

        # Add results for each of the requests
        for result in provider_results:
            if result.provider.id not in audit['providers']:
                audit['providers'][result.provider.id] = {
                    'id': result.provider.id,
                    'acronym': result.provider.acronym,
                    'name': result.provider.name,
                    'enrolment_samples': []
                }
            if result.request.id not in audit['requests']:
                req_result = result.request.requestresult_set.first()
                req_result_value = None
                req_result_status = None
                req_result_error_message = None
                req_result_message_code = None
                req_result_code = None
                if req_result is not None:
                    req_result_value = req_result.result
                    req_result_status = req_result.status
                    req_result_error_message = req_result.error_message
                    req_result_code = req_result.code
                    if req_result.message_code is not None:
                        req_result_message_code = req_result.message_code.code

                audit['requests'][result.request.id] = {
                    'id': result.request.id,
                    'created_at': result.request.created_at,
                    'error_message': result.request.error_message,
                    'session': result.request.session.id,
                    'result': req_result_value,
                    'status': req_result_status,
                    'error_message_res': req_result_error_message,
                    'message_code': req_result_message_code,
                    'code': req_result_code,
                    'results': {},
                }
                if result.request.message_code is not None:
                    audit['requests'][result.request.id]['message_code'] = result.request.message_code

                try:
                    request_data = json.loads(result.request.data.read().decode())
                    audit['requests'][result.request.id]['data'] = request_data['data']
                    audit['requests'][result.request.id]['metadata'] = request_data['metadata']
                except Exception:
                    audit['requests'][result.request.id]['data'] = None
                    audit['requests'][result.request.id]['metadata'] = None

            # Read the audit for this request
            try:
                provider_audit = json.loads(result.audit.read().decode())
            except Exception:
                provider_audit = None

            audit['requests'][result.request.id]['results'][result.provider.id] = {
                'status': result.status,
                'result': result.result,
                'audit': provider_audit
            }

        # Add enrolment data
        for provider_id in audit['providers']:
            enrolment = Enrolment.objects.get(provider_id=provider_id, learner=self.report.learner)
            for sample in enrolment.model_samples.filter(status=1).all():
                if sample.id not in audit['enrolment_samples']:
                    try:
                        sample_data = json.loads(sample.data.read().decode())
                    except Exception:
                        sample_data = None
                    audit['enrolment_samples'][sample.id] = sample_data
                audit['providers'][provider_id]['enrolment_samples'].append(sample.id)
                audit['providers'][provider_id]['enrolment_percentage'] = enrolment.percentage

        return audit
