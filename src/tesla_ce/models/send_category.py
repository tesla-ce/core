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
""" SENDCategory model module."""

from django.db import models
from django.utils.translation import gettext_lazy as _

from .base_model import BaseModel
from .institution import Institution


class SENDCategory(BaseModel):
    """ SENDCategory model. """
    institution = models.ForeignKey(Institution, null=False, on_delete=models.CASCADE,
                                    help_text=_('Institution this category is defined for'))
    description = models.TextField(null=False, blank=False,
                                   help_text=_("Category description."))

    data = models.TextField(null=False, blank=False,
                            help_text=_("Category configuration."))

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __repr__(self):
        return "<SENDCategory(id='%r', description='%s')>" % (
            self.id, self.description)
