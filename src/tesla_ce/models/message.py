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
""" Message model module."""

from django.db import models
from django.utils.translation import gettext_lazy as _

from .base_model import BaseModel


class Message(BaseModel):
    """ Message model. """
    code = models.CharField(max_length=50, null=False, blank=False, primary_key=True, help_text=_("Message code"))
    datatype = models.CharField(max_length=50, null=False, blank=False, default='html',
                                help_text=_("Type of the message"))
    description = models.TextField(null=True, blank=False, default=None,
                                   help_text=_("Description of the message for translation"))
    meaning = models.TextField(null=True, blank=False, default=None,
                               help_text=_("Meaning of the message for translation"))

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __repr__(self):
        return "<Message(code='%s')>" % (
            self.code
        )

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        self.code = self.code.upper()
        super().save(force_insert, force_update, using, update_fields)


class MessageLocale(BaseModel):
    """ Message model. """
    code = models.ForeignKey(Message, null=False, blank=False, on_delete=models.CASCADE, help_text=_("Message code"))
    locale = models.CharField(max_length=10, null=False, blank=False, help_text=_("Locale"))
    message = models.TextField(null=False, blank=False, help_text=_('Message'))
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = (('code', 'locale'),)

    def __repr__(self):
        return "<MessageLocale(code='%s', locale='%r', message='%r')>" % (
            self.code, self.locale, self.message
        )

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        self.locale = self.locale.lower()
        super().save(force_insert, force_update, using, update_fields)
