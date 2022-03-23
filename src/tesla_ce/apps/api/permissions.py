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
""" TeSLA API permissions module """
from rest_framework import permissions

from tesla_ce.models import InstitutionUser
from tesla_ce.models import User
from tesla_ce.models import AuthenticatedModule
from tesla_ce.models import Course


class GlobalAdminPermission(permissions.BasePermission):
    """
        Global admins have read only permissions
    """
    def has_permission(self, request, view):
        return request.user.is_staff


class GlobalAdminReadOnlyPermission(GlobalAdminPermission):
    """
        Global admins have read only permissions
    """
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return super().has_permission(request, view)

        return False


class InstitutionMemberPermission(permissions.BasePermission):
    """
        Only members of the institution can access to the view
    """

    def _get_user_institution(self, request):

        if not request.user.is_authenticated:
            return None

        if isinstance(request.user, InstitutionUser):
            return request.user.institution

        if isinstance(request.user, User):
            try:
                return request.user.institutionuser.institution
            except User.institutionuser.RelatedObjectDoesNotExist:
                return None

    def has_permission(self, request, view):

        institution = self._get_user_institution(request)

        if institution is None or not request.path.startswith('/api/{}/institution/{}/'.format(request.version,
                                                                                               institution.id)):
            return False
        return True


class InstitutionMemberReadOnlyPermission(InstitutionMemberPermission):
    """
        Only members of the institution can access to the view in read only mode
    """
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return super().has_permission(request, view)
        return False


class InstitutionAdminPermission(InstitutionMemberPermission):
    """
        Only admins of the institution can access to the view
    """
    def has_permission(self, request, view):
        if super().has_permission(request, view):
            if isinstance(request.user, InstitutionUser):
                return request.user.inst_admin
            else:
                return request.user.institutionuser.inst_admin

        return False


class InstitutionAdminReadOnlyPermission(InstitutionAdminPermission):
    """
        Only admins of the institution can access to the view in read only mode
    """
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return super().has_permission(request, view)
        return False


class InstitutionDataAdminPermission(InstitutionMemberPermission):
    """
        Only admins of the institution can access to the view
    """
    def has_permission(self, request, view):
        if super().has_permission(request, view):
            if isinstance(request.user, InstitutionUser):
                return request.user.data_admin
            else:
                return request.user.institutionuser.data_admin

        return False


class InstitutionDataAdminReadOnlyPermission(InstitutionDataAdminPermission):
    """
        Only admins of the institution can access to the view in read only mode
    """
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return super().has_permission(request, view)
        return False


class InstitutionLegalAdminPermission(InstitutionMemberPermission):
    """
        Only admins of the institution can access to the view
    """
    def has_permission(self, request, view):
        if super().has_permission(request, view):
            if isinstance(request.user, InstitutionUser):
                return request.user.legal_admin
            else:
                return request.user.institutionuser.legal_admin

        return False


class InstitutionLegalAdminReadOnlyPermission(InstitutionLegalAdminPermission):
    """
        Only admins of the institution can access to the view in read only mode
    """
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return super().has_permission(request, view)
        return False


class InstitutionSENDAdminPermission(InstitutionMemberPermission):
    """
        Only SEND admins of the institution can access to the view
    """
    def has_permission(self, request, view):
        if super().has_permission(request, view):
            if isinstance(request.user, InstitutionUser):
                return request.user.send_admin
            else:
                return request.user.institutionuser.send_admin

        return False


class InstitutionSENDAdminReadOnlyPermission(InstitutionSENDAdminPermission):
    """
        Only SEND admins of the institution can access to the view in read only mode
    """
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return super().has_permission(request, view)
        return False


class InstitutionLearnerPermission(InstitutionMemberPermission):
    """
        An institution learner accessing his/her information
    """
    def has_permission(self, request, view):
        if super().has_permission(request, view):
            return '/learner/{}/'.format(request.user.id) in request.path
        return False


class InstitutionLearnerReadOnlyPermission(InstitutionLearnerPermission):
    """
        An institution learner accessing his/her information in read only mode
    """
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return super().has_permission(request, view)
        return False


class InstitutionCourseInstructorPermission(InstitutionMemberPermission):
    """
        An institution instructor accessing his/her course information
    """
    def _get_course(self, request):
        """ Get the course that is accessed """
        institution = super()._get_user_institution(request)
        if institution is None:
            return None
        url_pattern = '/api/{}/institution/{}/course/'.format(request.version, institution.id)
        if request.path.startswith(url_pattern):
            course_part = request.path.split(url_pattern)
            if len(course_part) != 2:
                return None
            course_id_str = course_part[1].split('/')[0]
            try:
                course_id = int(course_id_str)
                return Course.objects.filter(vle__institution=institution).get(id=course_id)
            except TypeError:
                return None
            except Course.DoesNotExist:
                return None
        return None

    def has_permission(self, request, view):
        if super().has_permission(request, view):
            course = self._get_course(request)
            if course is None:
                return False
            try:
                return course.instructors.filter(id=request.user.id).count() == 1
            except Exception:
                return False
        return False


class InstitutionCourseInstructorReadOnlyPermission(InstitutionCourseInstructorPermission):
    """
        An institution instructor accessing his/her course information in read only mode
    """
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return super().has_permission(request, view)
        return False


class InstitutionCourseLearnerPermission(InstitutionMemberPermission):
    """
        An institution learner accessing his/her course information
    """
    def _get_course(self, request):
        """ Get the course that is accessed """
        institution = super()._get_user_institution(request)
        if institution is None:
            return None
        url_pattern = '/api/{}/institution/{}/course/'.format(request.version, institution.id)
        if request.path.startswith(url_pattern):
            course_part = request.path.split(url_pattern)
            if len(course_part) != 2:
                return None
            course_id_str = course_part[1].split('/')[0]
            try:
                course_id = int(course_id_str)
                return Course.objects.filter(vle__institution=institution).get(id=course_id)
            except TypeError:
                return None
            except Course.DoesNotExist:
                return None
        return None

    def has_permission(self, request, view):
        if super().has_permission(request, view):
            course = self._get_course(request)
            if course is None:
                return False
            try:
                return course.learners.filter(id=request.user.id).count() == 1
            except Exception:
                return False
        return False


class InstitutionCourseLearnerReadOnlyPermission(InstitutionCourseLearnerPermission):
    """
        An institution learner accessing his/her information in read only mode
    """
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return super().has_permission(request, view)
        return False


class VLEPermission(permissions.BasePermission):
    """
        Only target VLE can access to the view
    """

    def has_permission(self, request, view):

        if not isinstance(request.user, AuthenticatedModule):
            return False

        vle_id = None
        if request.user.type == 'vle':
            vle_id = request.user.pk

        if vle_id is None or not request.path.startswith('/api/{}/vle/{}/'.format(request.version, vle_id)):
            return False
        return True


class VLEReadOnlyPermission(VLEPermission):
    """
        Only the targeted VLE can access to the view in read only mode
    """
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return super().has_permission(request, view)
        return False


class ProviderPermission(permissions.BasePermission):
    """
        Only target Provider can access to the view
    """

    def has_permission(self, request, view):

        if not isinstance(request.user, AuthenticatedModule):
            return False

        provider_id = None
        if request.user.type == 'provider':
            provider_id = request.user.pk

        if provider_id is None or not request.path.startswith(
                '/api/{}/provider/{}/'.format(request.version, provider_id)
        ):
            return False
        return True


class ProviderReadOnlyPermission(ProviderPermission):
    """
        Only the targeted Provider can access to the view in read only mode
    """
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return super().has_permission(request, view)
        return False
