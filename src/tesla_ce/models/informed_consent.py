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
""" InformedConsent model module."""

from cache_memoize import cache_memoize
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from .base_model import BaseModel
from .institution import Institution


@cache_memoize(24 * 60 * 60)
def valid_version(version, current_version):
    """
        Check if a version is valid. To be valid, it should be the current version or a minor change
        :param version: The version to be checked
        :type version: str
        :param current_version: The current valid version
        :type current_version: str
        :return: True if the version is valid or False otherwise
        :rtype: bool
    """
    if version == current_version:
        return True
    version = [int(ver_part) for ver_part in version.split('.')]
    current_version = [int(ver_part) for ver_part in current_version.split('.')]
    if version[0] == current_version[0] and version[1] == current_version[1]:
        return True
    return False


@cache_memoize(24 * 60 * 60)
def get_current_ic_version(institution):
    """
        Get the current Informed Version for an institution
        :param institution: Institution object
        :type institution: Institution
        :return: Current version for this institution
        :rtype: str
    """
    institution_ic = InformedConsent.objects.filter(institution=institution,
                                                    valid_from__lte=timezone.now()
                                                    ).all()
    current_version = None
    for inst_ic in institution_ic:
        version = [int(ver_part) for ver_part in inst_ic.version.split('.')]
        if current_version is None:
            current_version = version
        else:
            if version[0] > current_version[0] or (
                version[0] == current_version[0]
                and version[1] > current_version[1]
            ) or (
                version[0] == current_version[0]
                and version[1] == current_version[1]
                and version[2] > current_version[2]
            ):
                current_version = version
    if current_version is not None:
        return '.'.join([str(ver_part) for ver_part in current_version])
    return None


class InformedConsent(BaseModel):
    """ InformedConsent model. """
    institution = models.ForeignKey(Institution, null=False, on_delete=models.CASCADE,
                                    help_text=_('Institution of the informed consent'))
    version = models.CharField(max_length=250, null=False, blank=False,
                               help_text=_("Informed consent version."))

    valid_from = models.DateTimeField(null=False, help_text="Informed consent valid from")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = (('institution', 'version'),)

    def __repr__(self):
        return "<InformedConsent(version='%s', valid_from='%r')>" % (
            self.version, self.valid_from)

    @property
    def status(self):
        """
            Informed consent status
            :return: Current status of this informed consent
            :rtype: str
        """
        if self.valid_from > timezone.now():
            return 'NOT_VALID_YET'
        current_version = get_current_ic_version(self.institution)
        if current_version == self.version:
            return 'VALID'
        elif valid_version(self.version, current_version):
            return 'VALID_NEED_UPDATE'
        return 'NOT_VALID'

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        super().save(force_insert, force_update, using, update_fields)
        # Invalidate cached value
        get_current_ic_version.invalidate(self.institution)
