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
    facts = serializers.SerializerMethodField()

    class Meta:
        model = ReportActivityInstrument
        fields = ["instrument", "enrolment", "confidence", "result", "identity_level", "instrument_acronym",
                  "content_level", "integrity_level", "learner_histogram", "activity_histogram",
                  "instrument_id", "instrument_polarity", "result_bean", "thresholds",
                  "prob_learner", "prob_context", "h_prob_learner", "h_prob_context", "facts"]

    @staticmethod
    def get_activity_histogram(instance):
        """
            Get the activity histogram
            :param instance: Report Activity Instrument
            :return: Histogram
        """
        return instance.get_activity_histogram()

    @staticmethod
    def get_learner_histogram(instance):
        """
            Get the learner histogram
            :param instance: Report Activity Instrument
            :return: Histogram
        """
        return instance.get_learner_histogram()

    @staticmethod
    def get_instrument_polarity(instance):
        """
            Return the instrument polarity
            :param instance: Report Activity Instrument
            :return: 1 for normal polarity and -1 if inverted polarity
        """
        return instance.get_instrument_polarity()

    @staticmethod
    def get_result_bean(instance):
        """
            Get the histogram bin where current result is included
            :param instance: Report Activity Instrument
            :return: Bin number
        """
        return instance.get_result_bean()

    @staticmethod
    def get_thresholds(instance):
        """
            Get the reference thresholds for current instrument
            :param instance: Report Activity Instrument
            :return: Reference thresholds
        """
        prov_thr = instance.instrument.provider_set.first()
        return {
            "warning_below": prov_thr.warning_below,
            "alert_below": prov_thr.alert_below
        }

    @staticmethod
    def get_prob_learner(instance):
        """
            Compute the probability to have current value for the learner
            :param instance: Report Activity Instrument
            :return: Probability value
        """
        return instance.get_prob_learner()

    @staticmethod
    def get_prob_context(instance):
        """
            Compute the probability to have current value in the context
            :param instance: Report Activity Instrument
            :return: Probability value
        """
        return instance.get_prob_context()

    @staticmethod
    def get_h_prob_learner(instance):
        """
            Compute the probability to have better value for the learner
            :param instance: Report Activity Instrument
            :return: Probability value
        """
        return instance.get_h_prob_learner()

    @staticmethod
    def get_h_prob_context(instance):
        """
            Compute the probability to have better value in the context
            :param instance: Report Activity Instrument
            :return: Probability value
        """
        return instance.get_h_prob_context()

    @staticmethod
    def get_facts(instance):
        """
            Get facts from results
            :param instance: Report Activity Instrument
            :return: Dictionary with facts
        """
        return instance.get_facts()


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
    data = serializers.FileField(read_only=True)

    class Meta:
        model = ReportActivity
        fields = ["id", "learner", "detail", "identity_level", "content_level", "integrity_level", "data"]
