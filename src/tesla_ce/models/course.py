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
""" Course model module."""

from django.db import models
from django.utils.translation import gettext_lazy as _

from .base_model import BaseModel
from .instructor import Instructor
from .learner import Learner
from .vle import VLE


class Course(BaseModel):
    """ Course model. """
    vle = models.ForeignKey(VLE, null=False, blank=False,
                            on_delete=models.CASCADE,
                            help_text=_('Course VLE.'))

    code = models.CharField(max_length=250, null=False, blank=False,
                            help_text=_("Course code."))

    vle_course_id = models.CharField(max_length=250, null=False, blank=False,
                                     help_text=_("Course id on the VLE."))

    description = models.TextField(null=True, blank=True,
                                   help_text=_("Course description."))

    start = models.DateTimeField(blank=True, null=True,
                                 help_text=_("When course starts"))

    end = models.DateTimeField(blank=True, null=True,
                               help_text=_("When course ends"))

    learners = models.ManyToManyField(Learner, blank=True, help_text=_('Course learners.'))
    instructors = models.ManyToManyField(Instructor, blank=True, help_text=_('Course instructors.'))

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = (('vle', 'vle_course_id'),)

    def __repr__(self):
        return "<Course(id='%r', vle_id='%r', vle_course_id='%r', code='%s')>" % (
            self.id, self.vle_id, self.vle_course_id, self.code)
