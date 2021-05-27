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
""" Test forms module """
from django import forms

from tesla_ce.models import Activity
from tesla_ce.models import Course
from tesla_ce.models import Learner
from tesla_ce.models import VLE


class TestInitializationForm(forms.Form):
    """
        Form to select the context from a vle call
    """
    vle = forms.ModelChoiceField(label='vle', queryset=VLE.objects.order_by('id').all())
    course = forms.ModelChoiceField(label='course', queryset=Course.objects.order_by('id').all())
    activity = forms.ModelChoiceField(label='activity', queryset=Activity.objects.order_by('id').all())

    learner = forms.ModelChoiceField(label='learner', queryset=Learner.objects.order_by('id').all())
    locale = forms.ChoiceField(label='locale', choices=(
        ('ca', 'Catalan'),
        ('es', 'Spanish'),
        ('en', 'English'),
        ('fi', 'Finnish'),
        ('tr', 'Turkish'),
        ('bg', 'Bulgarian'),
    ))


class TestActivityForm(forms.Form):
    """
        Form for the test activity
    """
    session_id = forms.HiddenInput()
