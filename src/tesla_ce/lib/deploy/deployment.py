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
""" TeSLA CE deployment module """
import abc

from django.template.loader import render_to_string

from tesla_ce.lib.exception import TeslaDeploymentException
from ..modules import get_modules


class BaseDeployment:
    """ Base class for deployments """

    def __init__(self, client):
        """
            Default constructor

            :param client: Client instance
            :type client: Client
        """
        self._client = client
        self._config = client.config.config

    @classmethod
    def get_instance(cls, client, orchestrator=None):
        """
            Get specific deployment object for selected orchestrator

            :param client: TeSLA Client instance
            :type client: Client
            :param orchestrator: Orchestrator to be used
            :type orchestrator: str
        """
        if orchestrator is None:
            orchestrator = client.config.config.get('DEPLOYMENT_ORCHESTRATOR')
        instance = None
        if orchestrator == 'swarm':
            instance = SwarmDeployment(client)

        if instance is None:
            raise TeslaDeploymentException('Invalid orchestrator "{}"'.format(orchestrator))

        return instance

    @abc.abstractmethod
    def get_deployment_scripts(self):
        """
            Generate deployment scripts for provided class

            :return: All required scripts and files for the deployment
            :rtype: dict
        """
        pass

    @abc.abstractmethod
    def get_services_scripts(self):
        """
            Generate services deployment scripts for provided class

            :return: All required scripts and files for the deployment of required services
            :rtype: dict
        """
        pass

    @abc.abstractmethod
    def get_vle_scripts(self, vle):
        """
            Generate VLE deployment scripts for provided class

            :param vle: The VLE instance
            :type vle: tesla_ce.models.VLE
            :return: All required scripts and files for the deployment of required services
            :rtype: dict
        """
        pass

    @abc.abstractmethod
    def get_status(self):
        """
            Get the deployment status

            :return: Deployment status
            :rtype: dict
        """
        pass

    @staticmethod
    def _remove_empty_lines(text):
        return '\n'.join([line for line in text.split('\n') if line.strip()])


class SwarmDeployment(BaseDeployment):

    def get_services_scripts(self):
        # Generate the context
        context = self._config.get_config_kv()

        # Generate services scripts
        files = {
            'tesla_services.yml': self._remove_empty_lines(render_to_string('deployment/swarm/tesla_services.yml',
                                                                            context)),
            'secrets/DB_ROOT_PASSWORD': context['DB_ROOT_PASSWORD'],
            'secrets/VAULT_DB_PASSWORD': context['VAULT_DB_PASSWORD'],
            'secrets/REDIS_PASSWORD': context['REDIS_PASSWORD'],
            'secrets/STORAGE_ACCESS_KEY': context['STORAGE_ACCESS_KEY'],
            'secrets/STORAGE_SECRET_KEY': context['STORAGE_SECRET_KEY'],
            'secrets/RABBITMQ_ADMIN_USER': context['RABBITMQ_ADMIN_USER'],
            'secrets/RABBITMQ_ADMIN_PASSWORD': context['RABBITMQ_ADMIN_PASSWORD'],
            'secrets/RABBITMQ_ERLANG_COOKIE': context['RABBITMQ_ERLANG_COOKIE'],
            'config/vault_config.json': self._remove_empty_lines(render_to_string('deployment/swarm/vault_config.json',
                                                                                  context)),
        }
        # Add loadbalancer script
        if self._config.get('DEPLOYMENT_LB') == 'traefik':
            files['tesla_lb.yml'] = self._remove_empty_lines(render_to_string('deployment/swarm/tesla_lb_traefik.yml',
                                                                              context))

        return files

    def get_deployment_scripts(self):
        # Generate the context
        context = self._config.get_config_kv()

        # Generate services scripts
        modules = get_modules()

        # Remove unnecessary workers
        if self._config.get('DEPLOYMENT_SPECIALIZED_WORKERS'):
            del modules['worker-all']
        else:
            del modules['worker-enrolment']
            del modules['worker-enrolment-storage']
            del modules['worker-enrolment-validation']
            del modules['worker-verification']
            del modules['worker-alerts']
            del modules['worker-reporting']

        context['services'] = [modules[module] for module in modules]
        files = {
            'tesla_core.yml': self._remove_empty_lines(render_to_string('deployment/swarm/tesla_core.yml',
                                                                        context)),
        }

        for module in modules:
            credentials = self._client.vault.get_module_credentials(module)
            files['secrets/{}_VAULT_ROLE_ID'.format(module.upper())] = credentials['role_id']
            files['secrets/{}_VAULT_SECRET_ID'.format(module.upper())] = credentials['secret_id']

        # Add loadbalancer script
        if self._config.get('DEPLOYMENT_LB') == 'traefik':
            files['tesla_lb.yml'] = self._remove_empty_lines(render_to_string('deployment/swarm/tesla_lb_traefik.yml',
                                                                              context))

        # Add Services script
        if self._config.get('DEPLOYMENT_SERVICES'):
            files['tesla_services.yml'] = self._remove_empty_lines(
                render_to_string('deployment/swarm/tesla_services.yml', context))

        # Add Front-end script
        files['tesla_dashboards.yml'] = self._remove_empty_lines(
            render_to_string('deployment/swarm/tesla_frontend.yml', context))

        return files

    def get_vle_scripts(self, vle):
        """
            Generate VLE deployment scripts for provided class

            :param vle: The VLE instance
            :type vle: tesla_ce.models.VLE
            :return: All required scripts and files for the deployment of required services
            :rtype: dict
        """
        # Generate the context
        context = self._config.get_config_kv()

        if context.get('MOODLE_ADMIN_EMAIL') is None:
            context['MOODLE_ADMIN_EMAIL'] = context['TESLA_ADMIN_MAIL']

        # Update VLE url
        vle.url = "https://moodle.{}".format(context['TESLA_DOMAIN'])
        vle.save()

        # Register the VLE
        vle_info = self._client.vault.register_vle(vle)

        # Generate vle scripts
        files = {
            'tesla_moodle.yml': self._remove_empty_lines(render_to_string('deployment/swarm/tesla_moodle.yml',
                                                                          context)),
            'secrets/MOODLE_DB_PASSWORD': context['MOODLE_DB_PASSWORD'],
            'secrets/MOODLE_ADMIN_PASSWORD': context['MOODLE_ADMIN_PASSWORD'],
            'secrets/MOODLE_ROLE_ID': vle_info['role_id'],
            'secrets/MOODLE_SECRET_ID': vle_info['secret_id'],
        }

        return files

    def get_status(self):
        return {
            'status': 0,
            'warnings': 0,
            'errors': 0,
            'info': {}
        }
