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
""" SENDLearner model module."""

from django.db import models

from .base_model import BaseModel
from .learner import Learner
from .learner import get_learner_send
from .send_category import SENDCategory


class SENDLearner(BaseModel):
    """ SENDLearner model. """
    learner = models.ForeignKey(Learner, null=False,
                                on_delete=models.CASCADE)
    category = models.ForeignKey(SENDCategory, null=False,
                                 on_delete=models.CASCADE)

    expires_at = models.DateTimeField(null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = (('learner', 'category'),)

    def __repr__(self):
        return "<SENDLearner(tesla_id='%r', category_id='%r')>" % (
            self.learner, self.category)

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        super().save(force_insert, force_update, using, update_fields)
        # Invalidate cached value
        get_learner_send.invalidate(self.learner_id)
