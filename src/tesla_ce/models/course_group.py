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
""" Course group model module."""

from django.db import models
from django.utils.translation import gettext_lazy as _

from .base_model import BaseModel
from .course import Course
from .institution import Institution


class CourseGroup(BaseModel):
    """ Course model. """
    institution = models.ForeignKey(Institution, null=False, blank=False,
                                    on_delete=models.CASCADE,
                                    help_text=_('Institution for this group.'))

    name = models.CharField(max_length=250, null=False, blank=False,
                            help_text=_("Group name."))

    description = models.TextField(null=True, blank=True,
                                   help_text=_("Group description."))

    parent = models.ForeignKey("self", null=True, blank=True,
                               on_delete=models.CASCADE,
                               related_name='children',
                               help_text=_('Parent group.'))

    courses = models.ManyToManyField(Course, blank=True,
                                     help_text=_('Courses in this group.'))

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __repr__(self):
        return "<CourseGroup(id='%r', institution_id='%r', name='%s')>" % (
            self.id, self.institution_id, self.name)
