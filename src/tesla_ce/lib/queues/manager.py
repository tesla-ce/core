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
#
""" Queue Manager Module"""
from ..config import ConfigManager


class QueueManager:
    """ Manager class for Queues """

    #: Queue Client
    _client = None

    def __init__(self, config=None):
        """
            Default constructor
            :param config: Configuration manager instance
            :type config: ConfigManager
        """
        if config is None:
            config = ConfigManager()

        # Store the configuration object
        self._config = config

    @property
    def client(self):
        """
            Access to the Queue client
            :return: Queue client object
            :rtype: BaseQueueClient
        """
        if self._client is None:
            if self._config.get_celery_config():
                pass

        return self._client

