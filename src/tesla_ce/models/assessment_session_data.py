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
""" Assessment session data model module."""
from django.db import models
from django.dispatch import receiver
from django.utils.translation import gettext_lazy as _

from .assessment_session import AssessmentSession
from .base_model import BaseModel


class AssessmentSessionData(BaseModel):
    """ Assessment session data model """
    session = models.OneToOneField(AssessmentSession, null=False,
                                   on_delete=models.CASCADE, help_text=_('Related assessment session'))

    connector = models.FileField(help_text=_('Connector JS file for this session'))

    data = models.FileField(help_text=_('Data for this session'))

    def __repr__(self):
        return "<AssessmentSessionData(session_id='%r')>" % (self.session_id)


@receiver(models.signals.post_delete, sender=AssessmentSessionData)
def auto_delete_file_on_delete(sender, instance, **kwargs):
    """
    Deletes file from filesystem
    when corresponding `FieldField` object is deleted.
    """
    if instance.connector:
        try:
            instance.connector.delete(save=False)
        except:
            pass

    if instance.data:
        try:
            instance.data.delete(save=False)
        except:
            pass
