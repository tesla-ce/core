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
""" Model module. """
from .activity import Activity
from .activity_instrument import ActivityInstrument
from .alert import Alert
from .assessment_session import AssessmentSession
from .assessment_session_data import AssessmentSessionData
from .course import Course
from .course_group import CourseGroup
from .enrolment import Enrolment
from .enrolment_sample import EnrolmentSample
from .enrolment_sample_validation import EnrolmentSampleValidation
from .histogram_activity_instrument import HistogramActivityInstrument
from .histogram_activity_provider import HistogramActivityProvider
from .histogram_learner_instrument import HistogramLearnerInstrument
from .histogram_learner_provider import HistogramLearnerProvider
from .informed_consent import InformedConsent
from .informed_consent_document import InformedConsentDocument
from .institution import Institution
from .instructor import Instructor
from .instrument import Instrument
from .launcher import Launcher
from .learner import Learner
from .message import Message
from .message import MessageLocale
from .monitor import Monitor
from .provider import Provider
from .provider_notification import ProviderNotification
from .report_activity import ReportActivity
from .report_activity_session import ReportActivitySession
from .report_activity_instrument import ReportActivityInstrument
from .request import Request
from .request_provider_result import RequestProviderResult
from .request_result import RequestResult
from .send_category import SENDCategory
from .send_learner import SENDLearner
from .ui_option import UIOption
from .user import AuthenticatedModule
from .user import AuthenticatedUser
from .user import InstitutionUser
from .user import UnauthenticatedUser
from .user import User
from .vle import VLE
from .webhooks import WebhookClient
from .webhooks import WebhookMessage

__all__ = [
    'Activity',
    'ActivityInstrument',
    'Alert',
    'Course',
    'Enrolment',
    'EnrolmentSample',
    'EnrolmentSampleValidation',
    'InformedConsent',
    'InformedConsentDocument',
    'Instrument',
    'Learner',
    'Message',
    'MessageLocale',
    'Monitor',
    'Instructor',
    'Provider',
    'ProviderNotification',
    'Request',
    'RequestResult',
    'RequestProviderResult',
    'SENDCategory',
    'SENDLearner',
    'VLE',
    'Institution',
    'AssessmentSession',
    'AssessmentSessionData',
    'InstitutionUser',
    'UnauthenticatedUser',
    'AuthenticatedModule',
    'AuthenticatedUser',
    'Launcher',
    'UIOption',
    'User',
    'ReportActivity',
    'ReportActivitySession',
    'ReportActivityInstrument',
    'HistogramActivityInstrument',
    'HistogramActivityProvider',
    'HistogramLearnerProvider',
    'HistogramLearnerInstrument',
    'WebhookClient',
    'WebhookMessage',
]
