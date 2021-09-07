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
""" TeSLA CE Instructor actions for Use Case tests """
import requests
from tests import auth_utils


def api_configure_activity(launcher, activity, providers):
    """
        An instructor configures the activity using the API
        :param launcher: Launcher object for an instructor
        :param activity: Activity object
        :param providers: List of enabled providers
    """
    # Authenticate with instructor launcher credentials
    client = auth_utils.client_with_launcher_credentials(launcher)

    # Get the user profile
    profile = auth_utils.get_profile(client)
    assert "INSTRUCTOR" in profile['roles']

    # Get required data
    institution_id = profile['institution']['id']
    course_id = activity['course']['id']
    activity_id = activity['id']

    # Add KS as main instrument
    instrument_id = providers['ks']['instrument']['id']
    ks_data = {
        'active': True,
        'instrument_id': instrument_id
    }
    ks_add_response = client.post(
        '/api/v2/institution/{}/course/{}/activity/{}/instrument/'.format(institution_id, course_id, activity_id),
        data=ks_data,
        format='json'
    )
    assert ks_add_response.status_code == 201
    # Add FR as an alternative instrument to KS
    instrument_id = providers['fr']['instrument']['id']
    fr_data = {
        'active': True,
        'options': {'online': True},
        'instrument_id': instrument_id,
        'alternative_to': ks_add_response.data['id']
    }
    fr_add_response = client.post(
        '/api/v2/institution/{}/course/{}/activity/{}/instrument/'.format(institution_id, course_id, activity_id),
        data=fr_data,
        format='json'
    )
    assert fr_add_response.status_code == 201
    # Add plagiarism as main instrument
    instrument_id = providers['plag']['instrument']['id']
    plag_data = {
        'active': True,
        'instrument_id': instrument_id
    }
    plag_add_response = client.post(
        '/api/v2/institution/{}/course/{}/activity/{}/instrument/'.format(institution_id, course_id, activity_id),
        data=plag_data,
        format='json'
    )
    assert plag_add_response.status_code == 201

    # Check that activity has now 3 instruments
    inst_list_response = client.get(
        '/api/v2/institution/{}/course/{}/activity/{}/instrument/'.format(institution_id, course_id, activity_id)
    )
    assert inst_list_response.status_code == 200
    assert inst_list_response.data['count'] == 3


def api_instructor_report(launcher, activity, filters=None):
    """
        Instructor review the results for the activity
        :param launcher: Instructor launcher object
        :param activity: Activity object
        :param filters: Filter reports
    """
    # Authenticate with instructor launcher credentials
    client = auth_utils.client_with_launcher_credentials(launcher)

    # Get the user profile
    profile = auth_utils.get_profile(client)
    assert "INSTRUCTOR" in profile['roles']

    # Get required data
    institution_id = profile['institution']['id']
    course_id = activity['course']['id']
    activity_id = activity['id']

    # Apply filters if provided
    url = '/api/v2/institution/{}/course/{}/activity/{}/report/'
    if filters is not None:
        url += '?{}'.format(filters)

    # Get the list of reports from the activity
    activity_reports_resp = client.get(url.format(
        institution_id,
        course_id,
        activity_id
    ))
    assert activity_reports_resp.status_code == 200
    reports = activity_reports_resp.data['results']

    # Get the detail for each report
    for report in reports:
        reports_detail_resp = client.get('/api/v2/institution/{}/course/{}/activity/{}/report/{}/'.format(
            institution_id,
            course_id,
            activity_id,
            report['id']
        ))
        assert reports_detail_resp.status_code == 200
        report['detailed_report'] = reports_detail_resp.data

        report_data_resp = requests.get(report['detailed_report']['data'], verify=False)
        assert report_data_resp.status_code == 200
        report['detailed_report']['data'] = report_data_resp.json()
        assert 'data' in report['detailed_report']
        assert 'sessions' in report['detailed_report']['data']

        request_list = []
        final = False
        while not final:
            report_requests = client.get(
                '/api/v2/institution/{}/course/{}/activity/{}/report/{}/request/?offset={}'.format(
                    institution_id,
                    course_id,
                    activity_id,
                    report['id'],
                    len(request_list)
            ))
            assert report_requests.status_code == 200
            request_list += report_requests.data['results']
            if len(request_list) >= report_requests.data['count']:
                final = True
        report['detailed_report']['requests'] = request_list

        # Get audit data for each instrument
        report['audit'] = {}
        for instrument in report['detail']:
            audit_resp = client.get(
                '/api/v2/institution/{}/course/{}/activity/{}/report/{}/audit/{}/'.format(
                    institution_id,
                    course_id,
                    activity_id,
                    report['id'],
                    instrument['instrument_id']
            ))
            assert audit_resp.status_code == 200
            report['audit'][instrument['instrument_id']] = audit_resp.data

    return reports
