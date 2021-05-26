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
""" Learner API Alerts tasks module """
import simplejson
from celery.exceptions import Reject
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage

from tesla_ce import celery_app
from tesla_ce import models
from tesla_ce.models.alert import get_alert_from_value


@celery_app.task(ignore_result=True)
def create_alert(level, activity_id, learner_id, path, raised_at, instruments=None, session_id=None):
    try:
        # Store the alert message
        learner = models.Learner.objects.get(learner_id=learner_id)
        req = models.Alert.objects.create(level=get_alert_from_value(level),
                                          learner_id=learner.id,
                                          activity_id=activity_id,
                                          data=path,
                                          session_id=session_id,
                                          raised_at=raised_at)
        # Add the instruments
        if instruments is not None:
            req.instruments.set(instruments)
            if len(instruments) != req.instruments.count():
                error = {
                    "message": 'Invalid instruments',
                }
                default_storage.save('{}.error'.format(path), ContentFile(simplejson.dumps(error).encode('utf-8')))
                req.status = 2
                req.error_message = error["message"]
                req.save()
                raise Reject("Invalid Instruments", requeue=False)
        default_storage.save('{}.valid'.format(path), ContentFile(simplejson.dumps({
            "message": "stored",
            "alert_id": req.id
        }).encode('utf-8')))
        return req.id
    except models.Learner.DoesNotExist:
        raise Reject("Invalid Learner", requeue=False)
