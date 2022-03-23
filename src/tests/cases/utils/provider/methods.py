#  Copyright (c) 2021 Xavier Baró
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
""" TeSLA CE Provider actions for Use Case tests """
import io
import mock
import random
import requests
import simplejson
import uuid

from django.utils import timezone

from tests import auth_utils
from tests.conftest import get_random_string

from ..worker import get_task_by_queue


def provider_validate_samples(providers, tasks):
    """
    Providers validate samples in their queues
    :param providers: Available providers
    :param tasks: Pending tasks to be processed
    :return: List of pending tasks
    """
    # List simulating the validation queue
    pending_tasks_validation = []

    def create_validation_summary(*args, **kwargs):
        pending_tasks_validation.append(('create_validation_summary', args, kwargs))

    # Split tasks in queues
    queues = get_task_by_queue(tasks)

    # Each provider should process their tasks
    for queue_name in queues:
        provider = None
        deferred = False
        # Get the provider with this queue
        for prov in providers:
            if providers[prov]['queue'] == queue_name:
                instrument_id = providers[prov]['instrument']['id']
                provider = providers[prov]['credentials']
                deferred = providers[prov]['deferred']
        assert provider is not None
        client, config = auth_utils.client_with_approle_credentials(provider['role_id'], provider['secret_id'])
        # Get the Provider ID from configuration
        provider_id = config['provider_id']

        task_count = 0
        for task in queues[queue_name]:
            # Get the parameters
            assert task[0] == 'validate_request'
            learner_id, sample_id, validation_id = task[1][0]
            learner_id = str(learner_id)

            # Get Sample information
            get_sample_resp = client.get('/api/v2/provider/{}/enrolment/{}/sample/{}/validation/{}/'.format(
                provider_id, learner_id, sample_id, validation_id)
            )
            assert get_sample_resp.status_code == 200
            sample = get_sample_resp.data

            # Download sample content
            sample_data_resp = requests.get(sample['sample']['data'], verify=False)
            assert sample_data_resp.status_code == 200
            sample['sample']['data'] = sample_data_resp.json()

            # Do validation
            val_result = {
                'status': (task_count % 2) + 1,  # Set half of the samples as not valid
                'error_message': None,
                'validation_info': {
                    'free_field1': 35,
                    'other_field':{
                        'status':3
                    }
                },
                'message_code_id': None,
                'contribution': 1.0 / (instrument_id * 2)  # We send four times samples than the instrument id
            }
            task_count +=1

            if deferred:
                # Deferred instrument
                samp_status_resp = client.post(
                    '/api/v2/provider/{}/enrolment/{}/sample/{}/validation/{}/status/'.format(
                        provider_id, learner_id, sample_id, validation_id),
                                              data={"status": 4},  # WAITING_EXTERNAL_SERVICE
                                              format='json'
                                              )
                assert samp_status_resp.status_code == 200
                def_validation_result = {
                    'status': 4,  # WAITING_EXTERNAL_SERVICE
                    'error_message': None,
                    'validation_info': None,
                    'message_code_id': None,
                    'contribution': None
                }
                def_result = {
                    'result': def_validation_result,
                    'status': 4,
                    'info': {
                        'info_field1': 56,
                        'info_other_field': 'test',
                        'test_data_for_notification': {
                            'type': 'validation',
                            'url': '/api/v2/provider/{}/enrolment/{}/sample/{}/validation/{}/'.format(
                                provider_id, learner_id, sample_id, validation_id
                            ),
                            'data': val_result
                        }
                    },
                    'learner_id': learner_id,
                    'sample_id': sample_id,
                    'validation_id': validation_id
                }
                # Set the result
                sample_deferred_validate_resp = client.put(def_result['info']['test_data_for_notification']['url'],
                                                           data=def_result['result'],
                                                           format='json')
                assert sample_deferred_validate_resp.status_code == 200

                # Send a notification request
                notification = {
                    'key': get_random_string(10),
                    'when': (timezone.now() + timezone.timedelta(seconds=-10)).isoformat(),  # Negative to ensure is due
                    'info': def_result['info']
                }
                send_notification_resp = client.post('/api/v2/provider/{}/notification/'.format(provider_id),
                                                     data=notification,
                                                     format='json')
                assert send_notification_resp.status_code == 201
            else:
                with mock.patch('tesla_ce.tasks.requests.enrolment.create_validation_summary.apply_async',
                                create_validation_summary):
                    send_validation_resp = client.put(
                        '/api/v2/provider/{}/enrolment/{}/sample/{}/validation/{}/'.format(
                            provider_id, learner_id, sample_id, validation_id),
                        data=val_result,
                        format='json'
                    )
                    assert send_validation_resp.status_code == 200

    return pending_tasks_validation


def provider_enrol_learners(providers, tasks):
    """
    Provider perform learners enrolment
    :param providers: Available providers
    :param tasks: Pending tasks to be processed
    :return: List of new pending tasks
    """
    # Split tasks in queues
    queues = get_task_by_queue(tasks)

    # Each provider should process their tasks
    for queue_name in queues:
        provider = None
        instrument_id = None
        deferred = False
        # Get the provider with this queue
        for prov in providers:
            if providers[prov]['queue'] == queue_name:
                instrument_id = providers[prov]['instrument']['id']
                provider = providers[prov]['credentials']
                deferred = providers[prov]['deferred']
        assert provider is not None
        assert instrument_id is not None
        client, config = auth_utils.client_with_approle_credentials(provider['role_id'], provider['secret_id'])
        # Get the Provider ID from configuration
        provider_id = config['provider_id']

        for task in queues[queue_name]:
            # Get the parameters
            assert task[0] == 'enrol_learner'
            learner_id, sample_id = task[1][0]
            learner_id = str(learner_id)
            task_id = uuid.uuid4()

            # Get the model
            get_model_resp = client.post(
                '/api/v2/provider/{}/enrolment/'.format(provider_id),
                data={
                     'learner_id': learner_id,
                     'task_id': str(task_id)
                },
                format='json'
            )
            assert get_model_resp.status_code == 201
            model = get_model_resp.data
            model_data = None
            if model is not None and model['model'] is not None:
                model_data_resp = requests.get(model['model'], verify=False)
                assert model_data_resp.status_code == 200
                model_data = model_data_resp.json()

            # Get validated samples
            final = False
            val_samples = []
            while not final:
                val_samples_resp = client.get('/api/v2/provider/{}/enrolment/{}/available_samples/'.format(
                    provider_id, learner_id))
                assert val_samples_resp.status_code == 200
                val_samples += val_samples_resp.data['results']
                if val_samples_resp.data['count'] <= len(val_samples):
                    final = True

            # If there is no sample, unlock the model
            if len(val_samples) == 0:
                unlock_resp = client.post('/api/v2/provider/{}/enrolment/{}/unlock/'.format(provider_id, learner_id),
                                          data={
                                              'token': task_id
                                          },
                                          format='json')
                assert unlock_resp.status_code == 200
                continue

            # Get sample validations
            for sample in val_samples:
                # Get available validations
                final = False
                sample['validations'] = []
                while not final:
                    sample_vals_resp = client.get('/api/v2/provider/{}/enrolment/{}/sample/{}/validation/'.format(
                        provider_id, learner_id, sample_id))
                    assert sample_vals_resp.status_code == 200
                    sample['validations'] += sample_vals_resp.data['results']
                    if sample_vals_resp.data['count'] <= len(sample['validations']):
                        final = True
                # Get the sample data
                sample_data_resp = requests.get(sample['data'], verify=False)
                assert sample_data_resp.status_code == 200
                sample['data'] = sample_data_resp.json()

            # Perform the enrolment
            if model_data is None:
                model_data = {}
            new_model_data = model_data
            if 'num_samples' not in new_model_data:
                new_model_data['num_samples'] = 0
            if 'instrument_id' not in new_model_data:
                new_model_data['instrument_id'] = instrument_id
            new_model_data['num_samples'] += len(val_samples)
            new_percentage = 0
            if 'percentage' in new_model_data:
                new_percentage = new_model_data['percentage']
            sample_list = []
            if 'used_samples' in model:
                sample_list = model['used_samples']
            for sample in val_samples:
                sample_list.append(sample['id'])
                for validation in sample['validations']:
                    new_percentage += validation['contribution']
            new_model_data['percentage'] = min(1.0, new_percentage)
            model['valid'] = True
            model['model'] = new_model_data
            model['can_analyse'] = True
            model['percentage'] = new_model_data['percentage']
            model['used_samples'] = sample_list

            enrolment_result = {
                'learner_id': learner_id,
                'task_id': task_id,
                'percentage': model['percentage'],
                'can_analyse': model['can_analyse'],
                'used_samples': model['used_samples'],
                'error_message': None
            }

            if deferred:
                def_enrolment_result = {
                    'status': 6,  # WAITING_EXTERNAL_SERVICE
                    'learner_id': learner_id,
                    'task_id': task_id
                }
                def_result = {
                    'result': def_enrolment_result,
                    'status': 6,
                    'model': model,
                    'info': {
                        'info_field1': 56,
                        'info_other_field': 'test',
                        'test_data_for_notification': {
                            'type': 'enrolment',
                            'url': '/api/v2/provider/{}/enrolment/{}/'.format(provider_id, learner_id),
                            'data': enrolment_result,
                            'model_data': {
                                'url': model['model_upload_url']['url'],
                                'data': model['model_upload_url']['fields'],
                                'file_content': model['model']
                            }
                        }
                    },
                    'learner_id': learner_id,
                    'sample_id': sample_id,
                    'task_id': task_id
                }
                # Set the result
                deferred_enrolment_resp = client.put(def_result['info']['test_data_for_notification']['url'],
                                                     data=def_result['result'],
                                                     format='json')
                assert deferred_enrolment_resp.status_code == 200

                # Send a notification request
                notification = {
                    'key': get_random_string(10),
                    'when': (timezone.now() + timezone.timedelta(seconds=-10)).isoformat(),  # Negative to ensure is due
                    'info': def_result['info']
                }
                send_notification_resp = client.post('/api/v2/provider/{}/notification/'.format(provider_id),
                                                     data=notification,
                                                     format='json')
                assert send_notification_resp.status_code == 201
            else:
                # Save the model data
                model_data_save_resp = requests.post(model['model_upload_url']['url'],
                                                     data=model['model_upload_url']['fields'],
                                                     files={
                                                         'file': io.StringIO(simplejson.dumps(model['model']))
                                                     }, verify=False)
                assert model_data_save_resp.status_code == 204

                # Save the model and unlock it
                model_save_resp = client.put('/api/v2/provider/{}/enrolment/{}/'.format(provider_id, learner_id),
                                             data={
                                                 'learner_id': learner_id,
                                                 'task_id': task_id,
                                                 'percentage': model['percentage'],
                                                 'can_analyse': model['can_analyse'],
                                                 'used_samples': model['used_samples']
                                             },
                                             format='json')
                assert model_save_resp.status_code == 200


def provider_verify_request(providers, tasks):
    """
        Providers verify the information from requests in their queues
        :param providers: Available providers
        :param tasks: Pending tasks to be processed
        :return: List of pending tasks
    """
    # List simulating the verification queue
    pending_tasks_verification = []

    def create_verification_summary_test(*args, **kwargs):
        pending_tasks_verification.append(('create_verification_summary', args, kwargs))

    # Split tasks in queues
    queues = get_task_by_queue(tasks)

    # Each provider should process their tasks
    for queue_name in queues:
        provider_creds = None
        instrument_id = None
        deferred = False
        # Get the provider with this queue
        for prov in providers:
            if providers[prov]['queue'] == queue_name:
                instrument_id = providers[prov]['instrument']['id']
                provider_creds = providers[prov]['credentials']
                deferred = providers[prov]['deferred']
        assert provider_creds is not None
        assert instrument_id is not None
        client, config = auth_utils.client_with_approle_credentials(provider_creds['role_id'],
                                                                    provider_creds['secret_id'])
        # Get the Provider ID from configuration
        provider_id = config['provider_id']

        for task in queues[queue_name]:
            # Get the parameters
            assert task[0] == 'verify_request'
            request_id, result_id = task[1][0]

            # Get the request
            get_request_resp = client.get('/api/v2/provider/{}/request/{}/'.format(provider_id, request_id))
            assert get_request_resp.status_code == 200
            request = get_request_resp.data
            learner_id = request['learner_id']

            # Get the provider data
            get_provider_resp = client.get('/api/v2/provider/{}/'.format(provider_id))
            assert get_provider_resp.status_code == 200
            provider = get_provider_resp.data

            # Get the model if necessary
            model_data = None
            if provider['instrument']['requires_enrolment']:
                # Download learner model
                get_model_resp = client.get('/api/v2/provider/{}/enrolment/{}/'.format(provider_id, learner_id))
                assert get_model_resp.status_code == 200
                model = get_model_resp.data
                assert model['can_analyse']

                # Get model data
                model_data_resp = requests.get(model['model'], verify=False)
                assert model_data_resp.status_code == 200
                model_data = model_data_resp.json()

            # Get request data
            request_data_resp = requests.get(request['request']['data'], verify=False)
            assert request_data_resp.status_code == 200
            request['request']['data'] = request_data_resp.json()

            # Instrument compute result without external services
            result_err = random.random() / 10.0  # Generate values with an error of maximum 10%
            if provider['inverted_polarity']:
                result = result_err
            else:
                result = 1.0 - result_err
            verification_result = {
                'status': 1,  # PROCESSED  (2 for ERROR)
                'error_message': None,
                'audit_data': {
                    'using_model': model_data is not None,
                    'some_other_field': get_random_string(15)
                },
                'result': result,
                'code': 1,  # OK  (2 WARNING, 3 ALERT)
                'message_code': None
            }

            # Perform verification
            if deferred:
                # Deferred instrument
                req_status_resp = client.post('/api/v2/provider/{}/request/{}/status/'.format(provider_id, request_id),
                                              data={"status": 7},  # WAITING_EXTERNAL_SERVICE
                                              format='json'
                                              )
                assert req_status_resp.status_code == 200
                def_verification_result = {
                    'status': 7,  # WAITING_EXTERNAL_SERVICE
                    'error_message': None,
                    'audit_data': {
                        'using_model': model_data is not None,
                        'some_other_field': get_random_string(15)
                    },
                    'result': None,
                    'code': 0,  # PENDING
                    'message_code': None
                }
                def_result = {
                    'result': def_verification_result,
                    'status': 7,
                    'info': {
                        'info_field1': 56,
                        'info_other_field': 'test',
                        'test_data_for_notification': {
                            'type': 'verification',
                            'url': '/api/v2/provider/{}/request/{}/'.format(provider_id, request_id),
                            'data': verification_result
                        }
                    },
                    'request_id': request_id,
                    'audit_data': {}
                }
                # Set the result
                req_deferred_verify_resp = client.put(def_result['info']['test_data_for_notification']['url'],
                                                      data=def_result['result'],
                                                      format='json')
                assert req_deferred_verify_resp.status_code == 200

                # Send a notification request
                notification = {
                    'key': get_random_string(10),
                    'when': (timezone.now() + timezone.timedelta(seconds=-10)).isoformat(),  # Negative to ensure is due
                    'info': def_result['info']
                }
                send_notification_resp = client.post('/api/v2/provider/{}/notification/'.format(provider_id),
                                                     data=notification,
                                                     format='json')
                assert send_notification_resp.status_code == 201
            else:
                with mock.patch('tesla_ce.tasks.requests.verification.create_verification_summary.apply_async',
                                create_verification_summary_test):
                    put_result_resp = client.put('/api/v2/provider/{}/request/{}/'.format(provider_id, request_id),
                                                 data=verification_result,
                                                 format='json'
                                             )
                    assert put_result_resp.status_code == 200

    return pending_tasks_verification


def provider_process_notifications(providers, tasks, expected_type):
    """
        Providers process the notifications in their queues
        :param providers: Available providers
        :param tasks: Pending tasks to be processed
        :param expected_type: Type of expected notifications
        :return: List of pending tasks
    """
    # List simulating the proper queue depending on type of notification
    pending_tasks = []

    def create_validation_summary_test(*args, **kwargs):
        pending_tasks.append(('create_validation_summary', args, kwargs))

    def create_verification_summary_test(*args, **kwargs):
        pending_tasks.append(('create_verification_summary', args, kwargs))

    # Split tasks in queues
    queues = get_task_by_queue(tasks)

    # Each provider should process their tasks
    for queue_name in queues:
        provider_creds = None
        instrument_id = None
        deferred = False
        # Get the provider with this queue
        for prov in providers:
            if providers[prov]['queue'] == queue_name:
                instrument_id = providers[prov]['instrument']['id']
                provider_creds = providers[prov]['credentials']
                deferred = providers[prov]['deferred']
        assert provider_creds is not None
        assert instrument_id is not None
        assert deferred
        client, config = auth_utils.client_with_approle_credentials(provider_creds['role_id'],
                                                                    provider_creds['secret_id'])
        # Get the Provider ID from configuration
        provider_id = config['provider_id']

        for task in queues[queue_name]:
            # Get the parameters
            assert task[0] == 'provider_notify'
            notification_id = task[1][0][0]

            # Get notification content
            get_notification_resp = client.get('/api/v2/provider/{}/notification/{}/'.format(provider_id,
                                                                                             notification_id))
            assert get_notification_resp.status_code == 200
            notification = get_notification_resp.data

            # Get the information required to process the notification
            notification_type = notification['info']['test_data_for_notification']['type']
            url = notification['info']['test_data_for_notification']['url']
            data = notification['info']['test_data_for_notification']['data']
            assert notification_type == expected_type
            # Process each request depending on their type
            if notification_type == 'validation':
                with mock.patch('tesla_ce.tasks.requests.enrolment.create_validation_summary.apply_async',
                                create_validation_summary_test):
                    put_result_resp = client.put(url,
                                                 data=data,
                                                 format='json'
                                                 )
                    assert put_result_resp.status_code == 200
            elif notification_type == 'enrolment':
                model_url = notification['info']['test_data_for_notification']['model_data']['url']
                model_data = notification['info']['test_data_for_notification']['model_data']['data']
                model_file_content = notification['info']['test_data_for_notification']['model_data']['file_content']

                # Save the model data
                model_data_save_resp = requests.post(model_url,
                                                     data=model_data,
                                                     files={
                                                         'file': io.StringIO(simplejson.dumps(model_file_content))
                                                     }, verify=False)
                assert model_data_save_resp.status_code == 204

                # Save the model and unlock it
                model_save_resp = client.put(url,
                                             data=data,
                                             format='json')
                assert model_save_resp.status_code == 200
            elif notification_type == 'verification':
                with mock.patch('tesla_ce.tasks.requests.verification.create_verification_summary.apply_async',
                                create_verification_summary_test):
                    put_result_resp = client.put(url,
                                                 data=data,
                                                 format='json'
                                                 )
                    assert put_result_resp.status_code == 200

            # Once processed, remove notification
            client.delete('/api/v2/provider/{}/notification/{}/'.format(provider_id, notification_id))

    return pending_tasks
