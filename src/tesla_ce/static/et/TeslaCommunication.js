/*
 * Copyright (c) 2020 Xavier Baró
 *
 *     This program is free software: you can redistribute it and/or modify
 *     it under the terms of the GNU Affero General Public License as
 *     published by the Free Software Foundation, either version 3 of the
 *     License, or (at your option) any later version.
 *
 *     This program is distributed in the hope that it will be useful,
 *     but WITHOUT ANY WARRANTY; without even the implied warranty of
 *     MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 *     GNU Affero General Public License for more details.
 *
 *     You should have received a copy of the GNU Affero General Public License
 *     along with this program.  If not, see <https://www.gnu.org/licenses/>.
 */
/*
    Module that deals with the communications with TeSLA
*/
var TeslaCommunication = (function (TeslaConnector) {
    /*
        Access to the TeSLA Core module
    */
    let _core_module = null;
    let _token = null;
    let _token_exp = null;
    let _api_url = null;
    let _request_send_freq = 500;
    let _alert_send_freq = 1000;
    let _request_status_freq = 10 * 1000;
    let _network_speed = [];
    let _network_speed_status = null;
    let _network_error = false;

    /*
        List of IDs with pending confirmation
    */
    let _pending_confirmations = [];

    /*
        Alert buffer. Contains alert messages ready to be sent.
    */
    let _alert_buffer = {
        'current_transmission': null,
        'current_start_at': null,
        'requests': [],
        'status': {
            'pending': 0,
            'sending': 0,
            'completed': 0,
            'error': 0
        }
    };

    /*
        Request buffer. Contains data requests ready to be sent.
    */
    let _request_buffer = {
        'current_transmission': null,
        'current_start_at': null,
        'requests': [],
        'status': {
            'pending': 0,
            'sending': 0,
            'completed': 0,
            'error': 0
        }
    };

    /*
    * Updates network speed
    *
    * Estimates the mean network speed and notify via events when changes are detected
    *
    * @param {float}  speed  Computed speed in Kb/s.
    */
    function updateNetworkSpeed(speed) {
        if (_network_error) {
            _network_error = false;
            _network_speed_status = -1;
            _core_module.raiseAlert('info', {
                type: 'CONNECTION_RECOVERED',
                module: 'TeslaCommunications',
                message: 'Connection recovered with server',
            }, false);

        }
        if (_network_speed.length >= 10) {
            _network_speed.pop();
        }
        _network_speed.push(parseFloat(speed));
        const speedAvg = arr => arr.reduce((a,b) => a + b, 0) / arr.length;
        let meanSpeed =  speedAvg(_network_speed);
        let newStatus = 0;
        if (meanSpeed > 5) {
            newStatus = 1;
        } else if (meanSpeed > 1) {
            newStatus = 2;
        } else {
            newStatus = 3;
        }
        if (_network_speed_status !== newStatus) {
            _core_module.raiseEvent('NETWORK_SPEED_CHANGE', {
                speed: meanSpeed,
                status: newStatus
            });
            _network_speed_status = newStatus;
        }
        console.log('New speed value: ' + speed + ' kb/s  => mean: ' + meanSpeed + ' kb/s [' + newStatus + ']');
    }

    /*
    * Create verification request body.
    *
    * Creates a JSON object with all the expected information for a verification request.
    *
    * @param {string}   data             Base64 encoded data for the request.
    * @param {string}   mimetype         Mimetype for the provided data.
    * @param {list}     instruments      List with the IDs of target instruments for this request.
    * @param {Object}   [context=null}   Additional context values.
    * @param {string}   [filename=null]  Filename for provided data.
    *
    * @return {Object} Body in JSON format ready to be sent.
    */
    function getVerificationRequestBody(data, mimetype, instruments, context=null, filename=null) {

        return {
	        learner_id: _core_module.getLearner()["learner_id"],
	        course_id: _core_module.getActivity()["course"]["id"],
	        activity_id: _core_module.getActivity()["id"],
            session_id: _core_module.getSessionId(),
            data : data,
            instruments: instruments,
            metadata: {
                filename: filename,
                mimetype: mimetype,
                context: context,
                created_at: Math.floor((new Date()).getTime() / 1000)
            }
        }
    }

    /*
    * Create enrolment request body.
    *
    * Creates a JSON object with all the expected information for an enrolment request.
    *
    * @param {string}   data             Base64 encoded data for the request.
    * @param {string}   mimetype         Mimetype for the provided data.
    * @param {list}     instruments      List with the IDs of target instruments for this request.
    * @param {Object}   [context=null}   Additional context values.
    * @param {string}   [filename=null]  Filename for provided data.
    *
    * @return {Object} Body in JSON format ready to be sent.
    */
    function getEnrolmentRequestBody(data, mimetype, instruments, context=null, filename=null) {

        return {
	        learner_id: _core_module.getLearner()["learner_id"],
            data : data,
            instruments: instruments,
            metadata: {
                filename: filename,
                mimetype: mimetype,
                context: context,
                created_at: Math.floor((new Date()).getTime() / 1000)
            }
        }
    }

    /*
    * Create alert message body.
    *
    * Creates a JSON object with all the expected information for an alert message.
    *
    * @param {string}   level          Level of the alert. Can be 'info', 'warning', 'alert'
    * @param {Object}   data           Object with alert information.
    * @param {list}     [instruments]  List with the IDs of involved instruments for this alert.
    *
    * @return {Object} Body in JSON format ready to be sent.
    */
    function getAlertBody(level, data, instruments=null) {
        return {
            level: level,
	        learner_id: _core_module.getLearner()["learner_id"],
            course_id: _core_module.getActivity()["course"]["id"],
	        activity_id: _core_module.getActivity()["id"],
            session_id: _core_module.getSessionId(),
            data : data,
            instruments: instruments,
            raised_at: new Date().toISOString()
        }
    }

    /*
    * Send a data to server
    *
    * Creates a data message and send it to the server.
    *
    * @param {string}   type                Type of data (enrolment, verification).
    * @param {string}   data                Base64 encoded data for the request.
    * @param {string}   mimetype            Mimetype for the provided data.
    * @param {list}     [instruments=null]  List with the IDs of target instruments for this request.
    * @param {Object}   [context=null]      Additional context values.
    * @param {string}   [filename=null]     Filename for provided data.
    */
    function sendData(type, data, mimetype, instruments=null, context=null, filename=null) {
        let body = null;
        if (type === 'enrolment') {
            body = getEnrolmentRequestBody(data, mimetype, instruments, context=null, filename=null);
        } else if (type === 'verification') {
            body = getVerificationRequestBody(data, mimetype, instruments, context=null, filename=null);
        } else {
            console.error('Invalid data type');
            return;
        }
        _request_buffer['requests'].push({
            type: type,
            institution_id: _core_module.getLearner()['institution_id'],
            learner_id: _core_module.getLearner()['learner_id'],
            body: body,
            retry_count: 0,
            transmit_start: null
        });
    }

    /*
    * Send alert message to server
    *
    * Creates an alert message and send it to the server.
    *
    * @param {string}   level               Level of the alert (info, warning, alert, error).
    * @param {Object}   data                Object with the alert description.
    * @param {list}     [instruments=null]  List with the IDs of target instruments involved on this alert.
    */
    function sendAlert(level, data, instruments=null) {
        _alert_buffer['requests'].push({
            institution_id: _core_module.getLearner()['institution_id'],
            learner_id: _core_module.getLearner()['learner_id'],
            body: getAlertBody(level, data),
            retry_count: 0,
            transmit_start: null
        });
    }

    /*
    * Refresh JWT token
    *
    * Refresh the current token
    */
    function refreshToken() {
        let xhr = new XMLHttpRequest();
        xhr.open("POST", _api_url + '/api/v2/auth/token/refresh', true);
        xhr.setRequestHeader('Authorization','JWT ' + _token['refresh_token']);
        xhr.setRequestHeader('Content-type','application/json; charset=utf-8');
        xhr.onload = function (evt) {
            if (xhr.readyState === 4 && xhr.status === 200) {
                _token = JSON.parse(xhr.response)['token'];
                _token_exp = JSON.parse(atob(_token['access_token'].split('.')[1]))['exp'] * 1000;
                // Launch renovation 1 minute before expiration
                let eta_ms = (new Date(_token_exp).getTime() - new Date()) - 60 * 1000;
                window.setTimeout(refreshToken, eta_ms);
            }
        }
        xhr.onerror = function (evt) {
            // Retry in 30 seconds
            window.setTimeout(refreshToken, 30 * 1000);
            _core_module.raiseEvent('NETWORK_ERROR', { });
        }
        xhr.send(JSON.stringify({token: _token['access_token']}));
    }

    /*
        Send pending request to server
    */
    function send_request_worker() {
        window.setTimeout(send_request_worker, _request_send_freq);
        if (_request_buffer['requests'].length === 0 || _request_buffer['current_transmission'] != null) {
            // There is no request to send or a request is being sent
            return;
        }
        // Get the request to transmit
        _request_buffer['current_transmission'] = _request_buffer['requests'].pop();
        _request_buffer['current_start_at'] = new Date();
        let type = _request_buffer['current_transmission']['type']
        let institution_id = _request_buffer['current_transmission']['institution_id'];
        let learner_id = _request_buffer['current_transmission']['learner_id'];
        let xhr = new XMLHttpRequest();
        xhr.open("POST", _api_url + '/lapi/v1/' + type + '/' + institution_id + '/' + learner_id + '/', true);
        xhr.setRequestHeader('Authorization','JWT ' + _token['access_token']);
        xhr.setRequestHeader('Content-type','application/json; charset=utf-8');
        xhr.onload = function (evt) {
            if (xhr.status === 401) {
                refreshToken();
            }
            if (xhr.readyState === 4 && xhr.status === 200) {
                // Store status path
                _pending_confirmations.push(JSON.parse(xhr.response)['path']);
                // Compute network speed
                let size = evt.total;
                let elapsed_time = new Date().getTime() - _request_buffer['current_start_at'].getTime();
                let speed = parseFloat(size / elapsed_time * 8.0).toFixed(2);
                updateNetworkSpeed(speed);

                // Empty current transmission
                _request_buffer['current_transmission'] = null;
                _request_buffer['current_start_at'] = null;
            }
        }
        xhr.onerror = function (evt) {
            // Re-enqueue to retry
            if (xhr.status > 0) {
                // When there is a connection error, do not increment the retry
                _request_buffer['current_transmission']['retry_count']++;
            }
            if (_request_buffer['current_transmission']['retry_count'] < 3) {
                _request_buffer['current_transmission']['transmit_start'] = null;
                _request_buffer['requests'].push(_request_buffer['current_transmission']);
                _request_buffer['current_transmission'] = null;
                _request_buffer['current_start_at'] = null;
            }
            _core_module.raiseEvent('NETWORK_ERROR', { });
        }
        xhr.send(JSON.stringify(_request_buffer['current_transmission']['body']));
    }

    /*
        Send pending alert to server
    */
    function send_alert_worker() {
        window.setTimeout(send_alert_worker, _alert_send_freq);
        if (_alert_buffer['requests'].length === 0 || _alert_buffer['current_transmission'] != null) {
            return;
        }
        // Get the alert to transmit
        _alert_buffer['current_transmission'] = _alert_buffer['requests'].pop();
        _alert_buffer['current_start_at'] = new Date();
        let institution_id = _alert_buffer['current_transmission']['institution_id'];
        let learner_id = _alert_buffer['current_transmission']['learner_id'];
        let xhr = new XMLHttpRequest();
        xhr.open("POST", _api_url + '/lapi/v1/alert/' + institution_id + '/' + learner_id + '/', true);
        xhr.setRequestHeader('Authorization','JWT ' + _token['access_token']);
        xhr.setRequestHeader('Content-type','application/json; charset=utf-8');
        xhr.onload = function (evt) {
            if (xhr.status === 401) {
                refreshToken();
            }
            if (xhr.readyState === 4 && xhr.status === 200) {
                // Store status path
                _pending_confirmations.push(JSON.parse(xhr.response)['path']);
                // Compute network speed
                let size = evt.total;
                let elapsed_time = new Date().getTime() - _alert_buffer['current_start_at'].getTime();
                let speed = parseFloat(size / elapsed_time * 8.0).toFixed(2);
                updateNetworkSpeed(speed);

                // Empty current transmission
                _alert_buffer['current_transmission'] = null;
                _alert_buffer['current_start_at'] = null;
            }
        }
        xhr.onerror = function (evt) {
            // Re-enqueue to retry
            if (xhr.status > 0) {
                // When there is a connection error, do not increment the retry
                _alert_buffer['current_transmission']['retry_count']++;
            }
            if (_alert_buffer['current_transmission']['retry_count'] < 3) {
                _alert_buffer['current_transmission']['transmit_start'] = null;
                _alert_buffer['requests'].push(_alert_buffer['current_transmission']);
                _alert_buffer['current_transmission'] = null;
                _alert_buffer['current_start_at'] = null;
            }
            _core_module.raiseEvent('NETWORK_ERROR', { });
        }
        xhr.send(JSON.stringify(_alert_buffer['current_transmission']['body']));
    }

    /*
        Check status of sent request
    */
    function request_status_worker() {
        window.setTimeout(request_status_worker, _request_status_freq);
        if (_pending_confirmations.length === 0) {
            return;
        }

        // Get the alert to transmit
        let institution_id = _core_module.getLearner()['institution_id'];
        let learner_id = _core_module.getLearner()['learner_id'];
        let xhr = new XMLHttpRequest();
        xhr.open("POST", _api_url + '/lapi/v1/status/' + institution_id + '/' + learner_id + '/', true);
        xhr.setRequestHeader('Authorization','JWT ' + _token['access_token']);
        xhr.setRequestHeader('Content-type','application/json; charset=utf-8');
        xhr.onload = function (evt) {
            if (xhr.status === 401) {
                refreshToken();
            }
            if (xhr.readyState === 4 && xhr.status === 200) {
                // Remove finished requests and send events in case of failure
                let responses = JSON.parse(xhr.response)
                for(let i=0; i<responses.length;i++) {
                    if (responses[i]['status'] !== "PENDING") {
                        let index = _pending_confirmations.indexOf(responses[i]['sample']);
                        if (index > -1) {
                            _pending_confirmations.splice(index, 1);
                        }
                        if (responses[i]['status'] !== "VALID") {
                            // TODO: Send event
                        }
                    }

                }
            }
        }
        xhr.onerror = function (evt) {
            _core_module.raiseEvent('NETWORK_ERROR', { });
        }
        xhr.send(JSON.stringify({
            learner_id: learner_id,
            samples: _pending_confirmations
        }));
    }

    function start() {
        window.setTimeout(send_request_worker, _request_send_freq);
        window.setTimeout(send_alert_worker, _alert_send_freq);
        window.setTimeout(request_status_worker, _request_status_freq);
    }

    function configure(core, config) {
        _core_module = core;
        _api_url = config['api_url'];
        _token = config['token'];
        _token_exp = JSON.parse(atob(_token['access_token'].split('.')[1]))['exp'] * 1000;
        _core_module.registerAlertHandler(function(alert) {
            sendAlert(alert['level'], alert);
        });
        _core_module.registerEventHandler(function(event) {
            if (event['type'] === 'NETWORK_ERROR') {
                if (!_network_error) {
                    _network_error = true;
                    _core_module.raiseAlert('error', {
                        type: 'CONNECTION_ERROR',
                        module: 'TeslaCommunications',
                        message: 'Connection lost with server',
                    });
                }
            }
        });

        // Program token refresh
        let eta_ms = new Date(_token_exp).getTime() - new Date();
        if (eta_ms < 60 * 1000) {
            refreshToken();
        } else {
            window.setTimeout(refreshToken, eta_ms);
        }

        // Start communication workers
        start();
    }

    TeslaConnector.registerModule("TeslaCommunication", {
        configure: configure,
        sendData: sendData
    });

	return TeslaConnector;
}(TeslaConnector || {}));
