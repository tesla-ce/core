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

from django.db import models
from django.utils.translation import gettext_lazy as _

from .base_model import BaseModel
from .instrument import Instrument
from .report_activity import REPORT_ALERT_LEVEL
from .report_activity import ReportActivity


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
