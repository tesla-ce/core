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
""" Api urls module """

from django.urls import include
from django.urls import path
from rest_framework_extensions.routers import ExtendedSimpleRouter

from . import views

# Create the base router
router = ExtendedSimpleRouter()

# VLE router
vle_router = router.register(r'vle', views.VLEViewSet, basename='vle')
vle_instrument_router = vle_router.register(r'instrument',
                                            views.VLEInstrumentViewSet,
                                            basename='vle-instrument',
                                            parents_query_lookups=['vle_id'])
vle_course_router = vle_router.register(r'course',
                                        views.VLECourseViewSet,
                                        basename='vle-course',
                                        parents_query_lookups=['vle_id'])
vle_course_activity_router = vle_course_router.register(r'activity',
                                                        views.VLECourseActivityViewSet,
                                                        basename='vle-course-activity',
                                                        parents_query_lookups=['vle_id', 'course_id'])

vle_course_activity_instrument_router = vle_course_activity_router.register(r'instrument',
                                                                            views.VLECourseActivityInstrumentViewSet,
                                                                            basename='vle-course-activity-instrument',
                                                                            parents_query_lookups=['vle_id',
                                                                                                   'course_id',
                                                                                                   'activity_id'])
vle_course_activity_learner_router = vle_course_activity_router.register(r'learner',
                                                                         views.VLECourseActivityLearnerViewSet,
                                                                         basename='vle-course-activity-learner',
                                                                         parents_query_lookups=['vle_id',
                                                                                                'course_id',
                                                                                                'activity_id'])
vle_course_activity_learner_request_router = vle_course_activity_learner_router.register(
    r'request',
    views.VLECourseActivityLearnerRequestViewSet,
    basename='vle-course-activity-learner-request',
    parents_query_lookups=['vle_id',
                           'course_id',
                           'activity_id',
                           'learner_id'
                           ])

vle_course_activity_report_router = vle_course_activity_router.register(
    r'report',
    views.VLECourseActivityReportViewSet,
    basename='vle-course-activity-report',
    parents_query_lookups=['activity__vle_id', 'activity__course_id', 'activity_id'])

vle_course_learner_router = vle_course_router.register(r'learner',
                                                       views.VLECourseLearnerViewSet,
                                                       basename='vle-course-learner',
                                                       parents_query_lookups=['vle_id', 'course_id'])
vle_course_instructor_router = vle_course_router.register(r'instructor',
                                                          views.VLECourseInstructorViewSet,
                                                          basename='vle-course-instructor',
                                                          parents_query_lookups=['vle_id', 'course_id'])

# Institution router
institution_router = router.register(r'institution', views.InstitutionViewSet, basename='institution')
# Institution => Informed consent routers
institution_ic_router = institution_router.register(r'ic',
                                                    views.InstitutionInformedConsentViewSet,
                                                    basename='institution-ic',
                                                    parents_query_lookups=['institution_id']
                                                    )
institution_ic_docs_router = institution_ic_router.register(r'document',
                                                            views.InstitutionInformedConsentDocumentViewSet,
                                                            basename='institution-ic-docs',
                                                            parents_query_lookups=['institution_id',
                                                                                   'informed_consent_id']
                                                    )

# Institution => Course Groups router
institution_course_group_router = institution_router.register(r'group',
                                                              views.InstitutionCourseGroupViewSet,
                                                              basename='institution-group',
                                                              parents_query_lookups=['institution_id']
                                                              )
institution_course_group_course_router = institution_course_group_router.register(
    r'course',
    views.InstitutionCourseGroupCourseViewSet,
    basename='institution-group-course',
    parents_query_lookups=['institution_id', 'id']
)
# Institution => SEND router
institution_send_router = institution_router.register(r'send',
                                                      views.InstitutionSENDCategoryViewSet,
                                                      basename='institution-send',
                                                      parents_query_lookups=['institution_id']
                                                      )

# Learner router
institution_learner_router = institution_router.register(r'learner',
                                                         views.InstitutionLearnerViewSet,
                                                         basename='institution-learner',
                                                         parents_query_lookups=['institution_id']
                                                         )

# Instructor router
institution_instructor_router = institution_router.register(r'instructor',
                                                            views.InstitutionInstructorViewSet,
                                                            basename='institution-instructor',
                                                            parents_query_lookups=['institution_id']
                                                            )

# Instrument router
institution_instrument_router = institution_router.register(r'instrument',
                                                            views.InstitutionInstrumentViewSet,
                                                            basename='institution-instrument',
                                                            parents_query_lookups=['institution_id']
                                                            )

# User Interface router
institution_ui_router = institution_router.register(r'ui',
                                                    views.InstitutionUIOptionViewSet,
                                                    basename='institution-ui',
                                                    parents_query_lookups=['institution_id']
                                                    )

# Course router
institution_course_router = institution_router.register(r'course',
                                                        views.InstitutionCourseViewSet,
                                                        basename='institution-course',
                                                        parents_query_lookups=['vle__institution_id']
                                                        )

institution_course_learner_router = institution_course_router.register(r'learner',
                                                                       views.InstitutionCourseLearnerViewSet,
                                                                       basename='institution-course-learner',
                                                                       parents_query_lookups=[
                                                                           'vle__institution_id',
                                                                           'id'
                                                                       ])

institution_course_instructor_router = institution_course_router.register(r'instructor',
                                                                          views.InstitutionCourseInstructorViewSet,
                                                                          basename='institution-course-instructor',
                                                                          parents_query_lookups=[
                                                                              'vle__institution_id',
                                                                              'id'
                                                                          ])

institution_course_activity_router = institution_course_router.register(r'activity',
                                                                        views.InstitutionCourseActivityViewSet,
                                                                        basename='institution-course-activity',
                                                                        parents_query_lookups=['vle__institution_id',
                                                                                               'course_id']
                                                                        )

institution_course_activity_instrument_router = institution_course_activity_router.register(
    r'instrument',
    views.InstitutionCourseActivityInstrumentViewSet,
    basename='institution-course-activity-instrument',
    parents_query_lookups=['activity__vle__institution_id',
                           'activity__course_id',
                           'activity_id']
)

institution_course_activity_report_router = institution_course_activity_router.register(
    r'report',
    views.InstitutionCourseActivityReportViewSet,
    basename='institution-course-activity-report',
    parents_query_lookups=['activity__vle__institution_id',
                           'activity__course_id',
                           'activity_id']
)

institution_course_activity_report_audit_router = institution_course_activity_report_router.register(
    r'audit',
    views.InstitutionCourseActivityReportAuditViewSet,
    basename='institution-course-activity-report-audit',
    parents_query_lookups=['report__activity__vle__institution_id',
                           'report__activity__course_id',
                           'report__activity_id',
                           'report_id']
)

institution_course_activity_report_requests_router = institution_course_activity_report_router.register(
    r'request',
    views.InstitutionCourseActivityReportRequestViewSet,
    basename='institution-course-activity-report-request',
    parents_query_lookups=['activity__vle__institution_id',
                           'activity__course_id',
                           'activity_id',
                           'id']
)

# VLE router
institution_vle = institution_router.register(r'vle',
                                              views.InstitutionVLEViewSet,
                                              basename='institution-vle',
                                              parents_query_lookups=['institution_id']
                                              )

# User router
institution_user = institution_router.register(r'user',
                                               views.InstitutionUserViewSet,
                                               basename='institution-user',
                                               parents_query_lookups=['institution_id']
                                               )

# Learner => SEND router
institution_learner_send_router = institution_learner_router.register(r'send',
                                                                      views.InstitutionSENDLearnerViewSet,
                                                                      basename='institution-learner-send',
                                                                      parents_query_lookups=['learner__institution_id',
                                                                                             'learner_id']
                                                                      )

# Administration API
# Instrument router
admin_user_router = router.register(r'admin/user', views.AdminUserViewSet, basename='admin-user')

# Instrument router
admin_instrument_router = router.register(r'admin/instrument', views.InstrumentViewSet, basename='admin-instrument')

# Instrument => Provider
instrument_provider_router = admin_instrument_router.register(r'provider',
                                                              views.AdminProviderViewSet,
                                                              basename='admin-instrument-provider',
                                                              parents_query_lookups=['instrument_id']
                                                              )
# Institution router
admin_institution_router = router.register(r'admin/institution', views.InstitutionAdminViewSet,
                                           basename='admin-institution')

# UI Option router
admin_ui_router = router.register(r'admin/ui', views.UIOptionViewSet,
                                  basename='admin-ui')


# Providers API
provider_router = router.register(r'provider', views.ProviderViewSet, basename='provider')

# Provider => Enrolment
provider_enrolment_router = provider_router.register(r'enrolment',
                                                     views.ProviderEnrolmentViewSet,
                                                     basename='provider-enrolment',
                                                     parents_query_lookups=['provider_id']
                                                     )
# Provider => Enrolment => Sample
provider_enrolment_sample_router = provider_enrolment_router.register(r'sample',
                                                                      views.ProviderEnrolmentSampleViewSet,
                                                                      basename='provider-enrolment-sample',
                                                                      parents_query_lookups=[
                                                                          'instruments__provider__id',
                                                                          'learner__learner_id'
                                                                      ])

# Provider => Enrolment => Sample => Validation
provider_enrolment_sample_validation_router = provider_enrolment_sample_router.register(
    r'validation',
    views.ProviderEnrolmentSampleValidationViewSet,
    basename='provider-enrolment-sample-validation',
    parents_query_lookups=['provider_id', 'sample__learner__learner_id', 'sample_id']
)

# Provider => Verification Request
provider_verification_router = provider_router.register(r'request',
                                                     views.ProviderVerificationRequestResultViewSet,
                                                     basename='provider-request',
                                                     parents_query_lookups=['provider_id']
                                                     )

# Provider => Notification
provider_notification_router = provider_router.register(r'notification',
                                                        views.ProviderNotificationViewSet,
                                                        basename='provider-notification',
                                                        parents_query_lookups=['provider_id']
                                                        )

app_name = 'tesla_ce.apps.api'
urlpatterns = [
    path('auth/', include('tesla_ce.apps.api.auth.urls')),
    path('', include(router.urls)),
]
