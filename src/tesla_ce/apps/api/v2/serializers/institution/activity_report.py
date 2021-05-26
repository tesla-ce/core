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
"""Activity Report api serialize module."""
from rest_framework import serializers

from tesla_ce.models import Learner
from tesla_ce.models import ReportActivity
from tesla_ce.models import ReportActivityInstrument


class InstitutionCourseActivityReportLearnerSerializer(serializers.ModelSerializer):
    """Activity Report Learner serialize model module."""
    class Meta:
        model = Learner
        fields = ["id", "uid", "first_name", "last_name", "email", "learner_id"]


class InstitutionCourseActivityReportDetailSerializer(serializers.ModelSerializer):
    """Activity Report Detail serialize model module."""
    instrument = serializers.CharField(source='instrument.name')
    instrument_id = serializers.IntegerField(source='instrument.id')
    enrolment = serializers.FloatField()
    confidence = serializers.FloatField()
    result = serializers.FloatField()

    class Meta:
        model = ReportActivityInstrument
        fields = ["instrument", "enrolment", "confidence", "result", "identity_level",
                  "content_level", "integrity_level", "instrument_id"]


class InstitutionCourseActivityReportExtendedDetailSerializer(serializers.ModelSerializer):
    """Activity Report Detail serialize model module."""
    instrument = serializers.CharField(source='instrument.name')
    instrument_id = serializers.IntegerField(source='instrument.id')
    instrument_acronym = serializers.CharField(source='instrument.acronym')
    instrument_polarity = serializers.SerializerMethodField()
    enrolment = serializers.FloatField()
    confidence = serializers.FloatField()
    result = serializers.FloatField()
    learner_histogram = serializers.SerializerMethodField()
    activity_histogram = serializers.SerializerMethodField()
    result_bean = serializers.SerializerMethodField()
    thresholds = serializers.SerializerMethodField()
    prob_learner = serializers.SerializerMethodField()
    prob_context = serializers.SerializerMethodField()
    h_prob_learner = serializers.SerializerMethodField()
    h_prob_context = serializers.SerializerMethodField()

    class Meta:
        model = ReportActivityInstrument
        fields = ["instrument", "enrolment", "confidence", "result", "identity_level", "instrument_acronym",
                  "content_level", "integrity_level", "learner_histogram", "activity_histogram",
                  "instrument_id", "instrument_polarity", "result_bean", "thresholds",
                  "prob_learner", "prob_context", "h_prob_learner", "h_prob_context"]

    @staticmethod
    def get_activity_histogram(instance):
        """
            Get the activity histogram
            :param instance: Report Activity Instrument
            :return: Histogram
        """
        return list(instance.instrument.histogramactivityinstrument_set.values_list(
            'b0', 'b1', 'b2', 'b3', 'b4', 'b5', 'b6', 'b7', 'b8', 'b9').first())

    @staticmethod
    def get_learner_histogram(instance):
        """
            Get the learner histogram
            :param instance: Report Activity Instrument
            :return: Histogram
        """
        return list(instance.report.learner.histogramlearnerinstrument_set.filter(
            instrument=instance.instrument
        ).values_list('b0', 'b1', 'b2', 'b3', 'b4', 'b5', 'b6', 'b7', 'b8', 'b9').first())

    @staticmethod
    def get_instrument_polarity(instance):
        return 2 * int(not instance.instrument.provider_set.first().inverted_polarity) - 1

    @staticmethod
    def get_result_bean(instance):
        return min(int(instance.result/10), 9)

    @staticmethod
    def get_thresholds(instance):
        prov_thr = instance.instrument.provider_set.first()
        return {
            "warning_below": prov_thr.warning_below,
            "alert_below": prov_thr.alert_below
        }

    def get_prob_learner(self, instance):
        """
            Compute the probability to have current value for the learner
            :param instance: Report Activity Instrument
            :return: Probability value
        """
        hist_bin = self.get_result_bean(instance)
        hist = self.get_learner_histogram(instance)
        acc = hist[hist_bin]
        if hist_bin > 0:
            acc += hist[hist_bin - 1] / 2.0
        if hist_bin < 9:
            acc += hist[hist_bin + 1] / 2.0

        return acc / sum(hist)

    def get_prob_context(self, instance):
        """
            Compute the probability to have current value in the context
            :param instance: Report Activity Instrument
            :return: Probability value
        """
        hist_bin = self.get_result_bean(instance)
        hist = self.get_activity_histogram(instance)
        acc = hist[hist_bin]
        if hist_bin > 0:
            acc += hist[hist_bin - 1] / 2.0
        if hist_bin < 9:
            acc += hist[hist_bin + 1] / 2.0

        return acc / sum(hist)

    def get_h_prob_learner(self, instance):
        """
            Compute the probability to have better value for the learner
            :param instance: Report Activity Instrument
            :return: Probability value
        """
        hist_bin = self.get_result_bean(instance)
        hist = self.get_learner_histogram(instance)
        if self.get_instrument_polarity(instance) > 0:
            acc = sum(hist[hist_bin + 1: 10])
        else:
            acc = sum(hist[0:hist_bin])

        return acc / sum(hist)

    def get_h_prob_context(self, instance):
        """
            Compute the probability to have better value in the context
            :param instance: Report Activity Instrument
            :return: Probability value
        """
        hist_bin = self.get_result_bean(instance)
        hist = self.get_activity_histogram(instance)
        if self.get_instrument_polarity(instance) > 0:
            acc = sum(hist[hist_bin + 1: 10])
        else:
            acc = sum(hist[0:hist_bin])

        return acc / sum(hist)


class InstitutionCourseActivityReportSerializer(serializers.ModelSerializer):
    """Activity Report serialize model module."""
    learner = InstitutionCourseActivityReportLearnerSerializer()
    detail = InstitutionCourseActivityReportDetailSerializer(source='reportactivityinstrument_set', many=True)

    class Meta:
        model = ReportActivity
        fields = ["id", "learner", "detail", "identity_level", "content_level", "integrity_level"]


class InstitutionCourseActivityReportExtendedSerializer(serializers.ModelSerializer):
    """Activity Report serialize model module."""
    learner = InstitutionCourseActivityReportLearnerSerializer()
    detail = InstitutionCourseActivityReportExtendedDetailSerializer(source='reportactivityinstrument_set', many=True)

    class Meta:
        model = ReportActivity
        fields = ["id", "learner", "detail", "identity_level", "content_level", "integrity_level"]
