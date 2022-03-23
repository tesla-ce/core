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
""" Vault Manager Module"""
import base64
import binascii
import datetime
import json
from typing import Union

import hvac
import pytz
from django.utils import timezone
from requests.exceptions import ConnectionError

from .setup import VaultSetup
from ..config import ConfigManager
from ..exception import TeslaVaultException
from ..modules import get_modules


class VaultManager:
    """ Manager class for Vault """

    #: Vault url
    vault_url: Union[str, None] = None

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

        # Check Vault URL
        self.vault_url = self._config.config.get('VAULT_URL')
        if not self.vault_url.startswith('http://') and not self.vault_url.startswith('https://'):
            raise TeslaVaultException('Invalid VAULT_URL value. Schema is expected.')

        # Initialize the Vault client
        self._client = hvac.Client(url=self.vault_url, verify=config.config.get('VAULT_SSL_VERIFY'))

        # Set root token if provided and management is enabled
        token = self._config.config.get('VAULT_TOKEN')
        if token is not None and self._config.config.get('VAULT_MANAGEMENT'):
            self._client.token = token

        # Set mount points
        self._approle_mount_point = self._config.config.get('VAULT_MOUNT_PATH_APPROLE')
        self._transit_mount_point = self._config.config.get('VAULT_MOUNT_PATH_TRANSIT')

        # Try to authenticate
        try:
            self._auth()
            self._is_ready = True
            self._error = None
        except TeslaVaultException as exc:
            self._is_ready = False
            self._error = exc

    def _module_auth(self):
        """
            Authenticate with vault using module credentials
        """
        # Authenticate with role and secret
        if not self._client.is_authenticated():
            role_id = self._config.config.get('VAULT_ROLE_ID')
            secret_id = self._config.config.get('VAULT_SECRET_ID')
            if role_id is None or secret_id is None:
                raise TeslaVaultException('Missing Vault module credentials')
            if isinstance(role_id, list) and len(role_id) != 1:
                raise TeslaVaultException('Multiple credentials not allowed on Vault Manager')
            self._client.auth.approle.login(role_id[0], secret_id[0],
                                            mount_point=self._config.config.get('VAULT_MOUNT_PATH_APPROLE'))

        # Check authentication
        if not self._client.is_authenticated():
            raise TeslaVaultException('Cannot authenticate with Vault')

    def _auth(self):
        """
            Perform authentication with Vault
        """
        try:
            if not self._client.sys.is_initialized() or self._client.sys.is_sealed():
                if not self._config.config.get('VAULT_MANAGEMENT'):
                    # Only management modules are able to work with not initialized or sealed vault instances
                    if not self._client.sys.is_initialized():
                        raise TeslaVaultException('Vault is not initialized when management is disabled.')
                    if self._client.sys.is_sealed():
                        raise TeslaVaultException('Vault is sealed when management is disabled.')
            else:
                # Management is disabled. Use module authentication.
                self._module_auth()
        except ConnectionError as conn_err:
            raise TeslaVaultException('Vault is not responding at {}.'.format(self.vault_url)) from conn_err

    def initialize(self):
        """
            Initialize Vault server
        """
        if not self._client.sys.is_initialized():
            # Initialize vault
            result = self._client.sys.initialize(5, 2)
            root_token = result['root_token']
            keys = result['keys']
            # Store token and keys
            self._config.config.set('VAULT_TOKEN', root_token)
            self._config.config.set('VAULT_KEYS', keys)
            # Store the credentials
            self._config.save_configuration()
            # Store token on client
            self._client.token = root_token

        if self._client.sys.is_sealed():
            # Unseal vault
            self.unseal(self._config.config.get('VAULT_KEYS'))

        if not self._client.sys.is_initialized() or self._client.sys.is_sealed():
            raise TeslaVaultException('Failed to initialize and unseal vault')

        # Setup vault information to be used in TeSLA
        self._setup_vault()

    def unseal(self, keys=None):
        """
            Unseal Vault server

            :param keys: Unseal keys for vault
        """
        if not self._client.sys.is_sealed():
            return
        # Get unseal keys
        if keys is None:
            keys = self._config.config.get('VAULT_KEYS')
        if keys is None:
            raise TeslaVaultException('Unseal keys not provided')
        self._client.sys.submit_unseal_keys(keys=keys)

    def _setup_vault(self):
        """
            Prepare Vault to be used by TeSLA. Creates the roles, configurations and policies.
        """
        # Create the setup object
        setup = VaultSetup(self._client, self._config.config)

        # Setup vault
        setup.run_setup()

    def get_module_credentials(self, module):
        """
            Generate new credentials for a given module

            :param module: Module name
            :type module: str
            :return: Object with the role_id and secret_id values
            :rtype: dict
        """
        # Check the module name
        if module not in get_modules() and not module.startswith('vle_') and not module.startswith('provider_'):
            raise TeslaVaultException('Invalid module name {}'.format(module))

        # Generate the new credentials
        role_id = self._client.auth.approle.read_role_id(module, mount_point=self._approle_mount_point)
        secret_id = self._client.auth.approle.generate_secret_id(module, mount_point=self._approle_mount_point)

        return {
            'role_id': role_id['data']['role_id'],
            'secret_id': secret_id['data']['secret_id']
        }

    def is_initialized(self):
        """
            Check if Vault is initialized

            :return: True if Vault is initialized or False otherwise
            :rtype: bool
        """
        return self._client.sys.is_initialized()

    def is_sealed(self):
        """
            Check if Vault is sealed

            :return: True if Vault is sealed or False otherwise
            :rtype: bool
        """
        return self._client.sys.is_sealed()

    def is_ready(self):
        """
            Check if Vault is ready to be used

            :return: True if Vault is ready or False otherwise
            :rtype: bool
        """
        return self.is_initialized() and not self.is_sealed()

    def create_token(self, data, ttl=120, key='default'):
        """
            Generates a JWT token that can be validated using VaultManager.

            :param data: Data to include in the token
            :type data: dict
            :param ttl: Validity time in minutes
            :type ttl: int
            :param key: The JWT key to be used for token generation
            :type key: str
            :return: JWT token
            :rtype: str
        """
        # Get current key
        key_name = 'jwt_{}'.format(key)
        try:
            jwt_signing_key = self._client.secrets.transit.read_key(name=key_name,
                                                                    mount_point=self._transit_mount_point)
            jwt_signing_key = jwt_signing_key['data']
        except hvac.exceptions.Forbidden:
            raise TeslaVaultException('Module not allowed to access JWT signing key {}'.format(key_name))

        # Build the header
        header = {
            'alg': "RS256",
            'typ': "JWT",
            'ver': '{}:v{}'.format(key, jwt_signing_key['latest_version'])
        }

        # Get current time and expiration
        current_time = timezone.now()
        expiration_time = current_time + timezone.timedelta(minutes=ttl)

        # Build payload with basic fields
        payload = {
            'iss': self.vault_url,
            'iat': int(current_time.timestamp()),
            'exp': int(expiration_time.timestamp()),
            'group': key,
        }

        # Add extra arguments to payload
        if data is not None:
            for arg in data:
                payload[arg] = data[arg]

        # Create the token
        b64_header = base64.urlsafe_b64encode(json.dumps(header).encode('utf8')).decode('ascii')
        b64_payload = base64.urlsafe_b64encode(json.dumps(payload).encode('utf8')).decode('ascii')
        b64_message = base64.b64encode('{}.{}'.format(b64_header, b64_payload).encode('utf8')).decode('ascii')

        # Sign the token
        try:
            sign_data_response = self._client.secrets.transit.sign_data(
                name=key_name,
                hash_input=b64_message,
                hash_algorithm='sha2-256',
                signature_algorithm='pkcs1v15',
                key_version=jwt_signing_key['latest_version'],
                mount_point=self._transit_mount_point,
            )
        except hvac.exceptions.Forbidden:
            raise TeslaVaultException('Module not allowed to sign JWT tokens with key {}'.format(key_name))

        signature = sign_data_response['data']['signature']

        # Extract the signature
        jws = signature.split(':')[2]
        b64_jws = base64.urlsafe_b64encode(jws.encode('utf8')).decode('ascii')

        # Build the token
        token = '{}.{}.{}'.format(b64_header, b64_payload, b64_jws)

        return token

    def validate_token(self, token):
        """
            Validate a JWT token

            :param token: Token to be validated
            :type token: str
            :return: Token validation data
            :rtype: dict
        """

        # Get token parts
        token_parts = token.split('.')

        if len(token_parts) != 3:
            raise TeslaVaultException('Invalid JWT format')

        # Get the data from the token
        try:
            header = json.loads(base64.urlsafe_b64decode(token_parts[0].encode('utf8')).decode('ascii'))
        except binascii.Error:
            raise TeslaVaultException('Invalid header encoding')
        try:
            payload = json.loads(base64.urlsafe_b64decode(token_parts[1].encode('utf8')).decode('ascii'))
        except binascii.Error:
            raise TeslaVaultException('Invalid payload encoding')

        # Get message for verification
        message = '{}.{}'.format(token_parts[0], token_parts[1])

        # Get key data
        key_ver = header['ver'].split(':')
        key_name = 'jwt_{}'.format(key_ver[0])
        key_version = key_ver[1]
        try:
            signature = base64.urlsafe_b64decode(token_parts[2]).decode('ascii')
        except binascii.Error:
            raise TeslaVaultException('Invalid signature encoding')
        signature = 'vault:{}:{}'.format(key_version, signature)

        # Verify token signature
        try:
            verify_signed_data_response = self._client.secrets.transit.verify_signed_data(
                name=key_name,
                hash_input=base64.urlsafe_b64encode(message.encode('utf8')).decode('ascii'),
                signature=signature,
                hash_algorithm='sha2-256',
                signature_algorithm='pkcs1v15',
                mount_point=self._transit_mount_point,
            )
        except hvac.exceptions.Forbidden:
            raise TeslaVaultException('Module not allowed to verify JWT tokens with key {}'.format(key_name))

        valid = verify_signed_data_response['data']['valid']
        if not valid:
            raise TeslaVaultException('Invalid Token Signature')

        # Check that the group is correct
        if key_ver[0] != payload['group']:
            raise TeslaVaultException('Invalid Payload group')

        # Check if token is expired
        expired = timezone.now() >= datetime.datetime.fromtimestamp(payload['exp'], tz=pytz.utc)
        if expired:
            raise TeslaVaultException('Token expired')

        return {
            'valid': valid,
            'payload': payload
        }


    def _build_jwt_token(self, key_name, key_version, header, payload):
        """
            Build a JWT token

            :param key_name: Name of the cryptographic key to be used
            :type key_name: str
            :param key_version: Version of the cryptographic key to be used
            :type key_version: str
            :param header: Token header data
            :type header: dict
            :param payload: Token payload data
            :type payload: dict
            :return: JWT token
        """

        # Create the token
        b64_header = base64.urlsafe_b64encode(json.dumps(header).encode('utf8')).decode('ascii')
        b64_payload = base64.urlsafe_b64encode(json.dumps(payload).encode('utf8')).decode('ascii')
        b64_message = base64.b64encode('{}.{}'.format(b64_header, b64_payload).encode('utf8')).decode('ascii')

        # Sign the token
        try:
            sign_data_response = self._client.secrets.transit.sign_data(
                name=key_name,
                hash_input=b64_message,
                hash_algorithm='sha2-256',
                signature_algorithm='pkcs1v15',
                key_version=key_version,
                mount_point=self._transit_mount_point,
            )
        except hvac.exceptions.Forbidden:
            raise TeslaVaultException('Module not allowed to sign JWT tokens with key {}'.format(key_name))

        signature = sign_data_response['data']['signature']

        # Extract the signature
        jws = signature.split(':')[2]
        b64_jws = base64.urlsafe_b64encode(jws.encode('utf8')).decode('ascii')

        # Build the token
        token = '{}.{}.{}'.format(b64_header, b64_payload, b64_jws)

        return token

    def refresh_token(self, access_token, refresh_token):
        """
            Refresh given token.

            :param access_token: The JWT token to be refreshed
            :type access_token: str
            :param refresh_token: The JWT refresh token authenticating this operation
            :type refresh_token: str
            :return: JWT token
            :rtype: str
        """
        # Verify token validity
        refresh_token_payload_resp = self.validate_token(refresh_token)
        refresh_token_payload = refresh_token_payload_resp['payload']

        # Get token parts
        refresh_token_parts = refresh_token.split('.')
        access_token_parts = access_token.split('.')

        refresh_token_header = json.loads(base64.b64decode(refresh_token_parts[0]))
        access_token_header = json.loads(base64.b64decode(access_token_parts[0]))
        access_token_payload = json.loads(base64.b64decode(access_token_parts[1]))

        # Check tokens compatibility
        if access_token_payload['type'] != refresh_token_payload['type'] \
            or access_token_payload['pk'] != refresh_token_payload['pk'] \
            or access_token_header['ver'].split(':')[0] != refresh_token_header['ver'].split(':')[0]:
            raise TeslaVaultException('Invalid refresh token')

        new_payload = access_token_payload
        del new_payload['iss']
        del new_payload['iat']
        del new_payload['exp']

        return self.create_token(new_payload, refresh_token_payload['ttl'], refresh_token_header['ver'].split(':')[0])

    def create_token_pair(self, data, ttl=15, max_ttl=120, key='default'):
        """
            Generates a JWT token pair that can be validated using VaultManager.

            :param data: Data to include in the token
            :type data: dict
            :param ttl: Validity time in minutes
            :type ttl: int
            :param max_ttl: Maximum time this token can be refreshed
            :type max_ttl: int
            :param key: The JWT key to be used for token generation
            :type key: str
            :return: JWT token
            :rtype: str
        """
        # Get current key
        key_name = 'jwt_{}'.format(key)
        try:
            jwt_signing_key = self._client.secrets.transit.read_key(name=key_name,
                                                                    mount_point=self._transit_mount_point)
            jwt_signing_key = jwt_signing_key['data']
        except hvac.exceptions.Forbidden:
            raise TeslaVaultException('Module not allowed to access JWT signing key {}'.format(key_name))

        # Build the header
        header = {
            'alg': "RS256",
            'typ': "JWT",
            'ver': '{}:v{}'.format(key, jwt_signing_key['latest_version'])
        }

        # Get current time and expiration
        current_time = timezone.now()
        expiration_time = current_time + timezone.timedelta(minutes=ttl)

        # Build payload with basic fields
        payload = {
            'iss': self.vault_url,
            'iat': int(current_time.timestamp()),
            'exp': int(expiration_time.timestamp()),
            'group': key,
        }

        # Add extra arguments to payload
        if data is not None:
            for arg in data:
                payload[arg] = data[arg]

        # Create the token
        access_token = self._build_jwt_token(key_name, jwt_signing_key['latest_version'], header, payload)

        # Fix the header and scope for the refresh token
        refresh_expiration_time = current_time + timezone.timedelta(minutes=max_ttl)
        payload['exp'] = int(refresh_expiration_time.timestamp())
        payload['scope'] = '/api/v2/auth/token/refresh'
        payload['ttl'] = ttl
        refresh_token = self._build_jwt_token(key_name, jwt_signing_key['latest_version'], header, payload)

        return {
            'access_token': access_token,
            'refresh_token': refresh_token
        }

    def verify_user_password(self, email, password):
        """
            Verify user credentials
        """
        # TODO: Check password on Vault
        if not email == password:
            raise TeslaVaultException('Invalid credentials')

        return {
            'email': email
        }

    def register_vle(self, vle):
        """
            Register or update information for a VLE

            :param vle: VLE model instance
            :type vle: tesla_ce.models.VLE
            :return: VLE connection options
            :rtype: dict
        """
        # Create the setup object
        setup = VaultSetup(self._client, self._config.config)

        # Create the new entity
        try:
            module_name = setup.register_vle(vle)

            # Generate new credentials for the VLE
            credentials = self.get_module_credentials(module_name)
            return {
                'role_id': credentials['role_id'],
                'secret_id': credentials['secret_id']
            }
        except hvac.exceptions.Forbidden as ex:
            raise TeslaVaultException('Operation not allowed', ex)

    def register_provider(self, provider):
        """
            Register or update information for a Provider

            :param provider: Provider model instance
            :type provider: tesla_ce.models.Provider
            :return: Provider connection options
            :rtype: dict
        """
        # Create the setup object
        setup = VaultSetup(self._client, self._config.config)

        # Create the new entity
        try:
            module_name = setup.register_provider(provider)

            # Generate new credentials for the Provider
            credentials = self.get_module_credentials(module_name)
            return {
                'role_id': credentials['role_id'],
                'secret_id': credentials['secret_id']
            }
        except hvac.exceptions.Forbidden:
            raise TeslaVaultException('Operation not allowed')

    def get_status(self):
        """
            Get the vault status

            :return: Object with status information
            :rtype: dict
        """
        return {
            'status': 0,
            'warnings': 0,
            'errors': 0,
            'info': {}
        }
