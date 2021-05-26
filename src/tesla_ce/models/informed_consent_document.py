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
""" InformedConsentDocument model module."""

from django.db import models
from django.utils.translation import gettext_lazy as _

from .base_model import BaseModel
from .informed_consent import InformedConsent


def get_upload_path(instance, filename):
    """
        Build the path where the informed consent document will be stored

        :param instance: Informed consent document
        :param filename: Name of the file
        :return: Path to store the file
    """
    return '{}/ic/{}/{}/{}'.format(
        instance.consent.institution.id,
        instance.consent.version,
        instance.language,
        filename
    )


class InformedConsentDocument(BaseModel):
    """ InformedConsentDocument model. """
    consent = models.ForeignKey(InformedConsent, null=False, blank=False,
                                on_delete=models.CASCADE)

    language = models.CharField(max_length=30, null=False, blank=False)

    html = models.TextField(null=True, blank=True,
                            help_text="HTML version of IC")

    pdf = models.FileField(null=True, blank=True, upload_to=get_upload_path,
                           help_text=_("PDF version of IC."))

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = (('consent', 'language'),)

    def __repr__(self):
        return "<InformedConsentDocument(consent_id='%d', language='%s')>" % (
            self.consent.id, self.language)
