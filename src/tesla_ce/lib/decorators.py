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
""" TeSLA decorators """
from functools import wraps

from django.conf import settings

from .exception import TeslaConfigException


def tesla_mode_required(modes):
    """
        Decorator to restrict the use of methods to a list of tesla running modes.

        :param function: Function to be decorated
        :param modes: List of modes. If not provided, method is restricted only to production
        :type modes: list
    """
    def decorator(function):
        @wraps(function)
        def _wrapped_function(*args, **kwargs):
            valid_modes = modes
            if valid_modes is None:
                valid_modes = ['production']
            if not isinstance(valid_modes, list):
                valid_modes = [valid_modes]
            current_mode = settings.TESLA_CONFIG.config.get('TESLA_MODE')
            if current_mode not in valid_modes:
                raise TeslaConfigException('Method not allowed in {} mode.'.format(current_mode))
            return function(*args, **kwargs)
        return _wrapped_function
    return decorator
