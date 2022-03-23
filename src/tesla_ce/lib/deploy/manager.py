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
""" Deployment Manager Module"""
import requests
from simplejson.errors import JSONDecodeError
from .deployment import BaseDeployment


class DeploymentManager:
    """ Manager class for Deployment """

    def __init__(self, client):
        """
            Default constructor
            :param client: Client instance
            :type client: Client
        """
        # Store the client
        self._client = client

        # Store the configuration object
        self._config = client.config

        # Create an instance of the deployment object
        self._deploy = BaseDeployment.get_instance(self._client)

    def get_status(self):
        """
            Get the deployment status

            :return: Object with status information
            :rtype: dict
        """
        return self._deploy.get_status()

    def get_deployment_scripts(self, orchestrator=None):
        """
            Get the deployment scripts according to the selected orchestrator

            :param orchestrator: The orchestrator to be used
            :type orchestrator: str
            :return: Object with all scripts and required files
            :rtype: dict
        """
        # Generate the deployment scripts
        if orchestrator is not None:
            instance = BaseDeployment.get_instance(self._client, orchestrator)
            return instance.get_deployment_scripts()
        return self._deploy.get_deployment_scripts()

    def get_services_deployment_scripts(self, orchestrator=None):
        """
            Get the services deployment scripts according to the selected orchestrator

            :param orchestrator: The orchestrator to be used
            :type orchestrator: str
            :return: Object with all scripts and required files
            :rtype: dict
        """
        # Generate the services deployment scripts
        if orchestrator is not None:
            instance = BaseDeployment.get_instance(self._client, orchestrator)
            return instance.get_services_scripts()
        return self._deploy.get_services_scripts()

    def get_vle_deployment_scripts(self, vle, orchestrator=None):
        """
            Get the vle deployment scripts according to the selected orchestrator

            :param vle: The VLE instance
            :type vle: tesla_ce.models.VLE
            :param orchestrator: The orchestrator to be used
            :type orchestrator: str
            :return: Object with all scripts and required files
            :rtype: dict
        """
        # Generate the VLE deployment scripts
        if orchestrator is not None:
            instance = BaseDeployment.get_instance(self._client, orchestrator)
            return instance.get_vle_scripts(vle)
        return self._deploy.get_vle_scripts(vle)

    def get_provider_deployment_scripts(self, provider, orchestrator=None, credentials=None):
        """
            Get the provider deployment scripts according to the selected orchestrator

            :param provider: The Provider instance
            :type provider: tesla_ce.models.Provider
            :param orchestrator: The orchestrator to be used
            :type orchestrator: str
            :param credentials: List of credentials required by this provider
            :type credentials: list
            :return: Object with all scripts and required files
            :rtype: dict
        """
        # Generate the VLE deployment scripts
        if orchestrator is not None:
            instance = BaseDeployment.get_instance(self._client, orchestrator)
            return instance.get_provider_scripts(provider, credentials)
        return self._deploy.get_provider_scripts(provider, credentials)

    @staticmethod
    def get_registered_providers(repository="tesla-ce/core", version="main"):
        """
            Get the list of registered providers

            :param repository: The repository in GitHub
            :type repository: str
            :param version: The branch on the repository
            :type version: str
            :return: List of registered providers
            :rtype: list
        """
        # Read registry of providers on the repository
        response = requests.get('https://raw.githubusercontent.com/{}/{}/providers/registry.json'.format(repository,
                                                                                                         version))
        if response.status_code != 200:
            return []

        resp_providers = response.json()

        providers = []
        for provider in resp_providers:
            provider_info_resp = requests.get(provider['url'])
            if provider_info_resp.status_code == 200:
                try:
                    providers.append(provider_info_resp.json())
                except JSONDecodeError:
                    # When fails to parse, do not include in the list
                    pass

        return providers
