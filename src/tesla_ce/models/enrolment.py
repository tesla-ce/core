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
""" Enrolment model module."""

from django.db import models
from django.utils.translation import gettext_lazy as _

from .base_model import BaseModel
from .enrolment_sample import EnrolmentSample
from .learner import Learner
from .learner import get_learner_enrolment
from .provider import Provider


def get_upload_path(instance, filename):
    """
        Build the path where the informed consent document will be stored

        :param instance: Informed consent document
        :type instance: Enrolment
        :param filename: Name of the file
        :return: Path to store the file
    """
    return '{}/models/{}/{}/{}.json'.format(
        instance.learner.institution.id,
        instance.learner.learner_id,
        instance.provider.instrument.id,
        instance.provider.id
    )


class Enrolment(BaseModel):
    """ Enrollment model. """
    learner = models.ForeignKey(Learner, null=False,
                                on_delete=models.CASCADE,
                                help_text=_("Related learner"))

    provider = models.ForeignKey(Provider, null=False,
                                 on_delete=models.CASCADE,
                                 help_text=_("Related provider"))

    percentage = models.DecimalField(null=False, decimal_places=2,
                                     max_digits=5,
                                     help_text=_("Percentage of enrolment for this learner"))

    can_analyse = models.BooleanField(null=False, default=False,
                                      help_text=_("This provider can verify learner samples"))

    locked_at = models.DateTimeField(null=True, default=None,
                                     help_text=_("This model is locked for an update process"))

    locked_by = models.UUIDField(null=True, default=None, blank=None,
                                 help_text=_("Task blocking this model"))

    model = models.FileField(max_length=250, null=True, default=None, upload_to=get_upload_path,
                             help_text=_('Path to stored model'))

    model_samples = models.ManyToManyField(EnrolmentSample, related_name='models',
                                           help_text=_('Enrolment samples used to create this model'))

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = (('learner', 'provider'),)

    @property
    def is_locked(self):
        return self.locked_at is not None and self.locked_by is not None

    @property
    def model_total_samples(self):
        return self.model_samples.count()

    def __repr__(self):
        return "<Enrollment(learner='%s', provider='%r', percentage='%r'," \
               "can_analyse='%s', locked='%r', num_samples='%r')>" % (self.learner, self.provider, self.percentage,
                                                                      self.can_analyse, self.is_locked,
                                                                      self.model_total_samples)

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        super().save(force_insert, force_update, using, update_fields)
        # Invalidate cached value
        get_learner_enrolment.invalidate(self.learner_id)
