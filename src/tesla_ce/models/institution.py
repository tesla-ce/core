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
""" Institution model module."""

from django.db import models
from django.utils.translation import gettext_lazy as _

from .base_model import BaseModel


class Institution(BaseModel):
    """ Institution model. """
    id = models.AutoField(null=False, unique=True, blank=False, primary_key=True,
                          help_text=_('Institution Id'))
    acronym = models.CharField(max_length=255, null=False, blank=False, unique=True,
                               help_text=_('Institution acronym'))
    name = models.TextField(blank=None, null=None, help_text=_('Name of the institution'))
    external_ic = models.BooleanField(null=None, default=False,
                                      help_text=_('Informed Consent is managed externally to TeSLA'))
    mail_domain = models.CharField(max_length=255, null=True, blank=True, default=None,
                                   help_text=_('Accepted mail domains for this institution'))
    disable_vle_learner_creation = models.BooleanField(null=None, default=False,
                                                       help_text=_('If enabled, VLEs cannot create learners'))
    disable_vle_instructor_creation = models.BooleanField(null=None, default=False,
                                                          help_text=_('If enabled, VLE cannot create instructors'))
    disable_vle_user_creation = models.BooleanField(null=None, default=False,
                                                    help_text=_('If enabled, VLE cannot create institution users'))
    allow_learner_report = models.BooleanField(null=None, default=False,
                                               help_text=_('Learners can access their reports'))
    allow_learner_audit = models.BooleanField(null=None, default=False,
                                              help_text=_('Learners can access the audit data of their reports'))
    allow_valid_audit = models.BooleanField(null=None, default=False,
                                            help_text=_('Audit data is available even when results are valid'))

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __repr__(self):
        return "<Institution(id='%r', acronym='%r', name='%r', external_ic='%r')>" % (
            self.id, self.acronym, self.name, self.external_ic)
