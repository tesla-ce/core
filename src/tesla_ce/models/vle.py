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
""" VLE model module."""
from django.db import models
from django.utils.translation import gettext_lazy as _

from .base_model import BaseModel
from .institution import Institution

# VLE types
VLE_TYPE = (
    (0, _('MOODLE')),
)


def get_type_id(name):
    """
        Get the vle type ID from vle name
        :param name: VLE type name
        :return: Vle type ID
    """
    for vle_type in VLE_TYPE:
        if vle_type[1].upper() == name.upper():
            return vle_type[0]
    return None


class VLE(BaseModel):
    """ VLE model. """
    name = models.CharField(max_length=250, null=False, blank=False, unique=True,
                            help_text=_("VLE unique name."))
    type = models.IntegerField(choices=VLE_TYPE, null=False, default=0, help_text=_('Type of the VLE.'))
    institution = models.ForeignKey(Institution, null=False, on_delete=models.CASCADE,
                                    help_text=_('Institution this VLE belongs to.'))
    url = models.TextField(null=True, blank=True, help_text=_("VLE url."))
    lti = models.TextField(null=True, blank=True, help_text=_("VLE lti configuration."))
    client_id = models.CharField(max_length=250, null=True, blank=False, default=None,
                                 help_text=_("LTI 1.3 Client ID."))

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __repr__(self):
        return "<VLE(id='%r', type='%r', name='%s')>" % (
            self.id, self.get_type_display(), self.name)
