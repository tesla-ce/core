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
var TeslaCore = (function (TeslaConnector) {
    /*
        Main module to connect with TeSLA
     */
    // System status
    let _status = {
        // Status level ('error', 'warning', 'ok')
        level: 'error',
        // Connected with Learner's API
        isConnected: false,
        // Successfully Authenticated
        isAuthenticated: false,
        // Whether learner accepted ethical warning
        isEthicalWarningAccepted: false,
        // Instruments are capturing data
        isCapturing: false,
        // Computed connection speed
        connectionSpeed: 0,
        // Pending data packages to be sent
        bufferSize: 0,
        // Registered Modules
        modules: new Map(),
    };

    /*
    * Detect when console is open
    */
    let checkStatus = null;
    let oldCheckStatus = null;
    let checkElement = new Image();

    function checkStatusChange() {
        if (checkStatus !== oldCheckStatus) {
            oldCheckStatus = checkStatus;
            if (checkStatus === 'on') {
                _status['modules'].get('TeslaEvents').raiseAlert('DETECTED_OPEN_CONSOLE', {});
            }
        }
    }


    // Configuration
    let _config = null

    function getLearner() {
        return _config['learner'];
    }

    function getLogoUrl() {
        return _config['logo_url'];
    }

    function getDashboardUrl() {
        return _config['dashboard_url'];
    }

    function getActivity() {
        return _config['activity'];
    }

    function isActive() {
        return _config['activity']['enabled'] && _config['instruments'].length > 0
    }

    function getInstruments() {
        return _config['instruments'];
    }

    function getSessionId() {
        return _config['session_id'];
    }

    function showEthicalWarning(allowReject, instruments, resolve, reject) {
        return _status['modules'].get('TeslaEthicalWarning').showEthicalWarning(allowReject, instruments, resolve, reject);
    }

    function showMenu(instruments, logo_url=null, dashboard_url=null) {
        return _status['modules'].get('TeslaFloatingMenu').showMenu(instruments, logo_url, dashboard_url);
    }

    function startCapture() {
        _status['modules'].forEach(function(mod) {
            if ( 'startCapture' in mod) {
                mod.startCapture();
            }
        });
    }

    function stopCapture() {
        _status['modules'].forEach(function(mod) {
            if ( 'stopCapture' in mod) {
                mod.stopCapture();
            }
        });
    }

    function stop() {
        // Stop capturing new data
        stopCapture()
        // Wait for pending data to be sent
        // TODO: Block execution while data is not sent
    }

    function run(config, modules) {
        // Store configuration and registered modules
        _config = config;
        _status['modules'] = modules;

        let exported_methods = {
            raiseEvent: _status['modules'].get('TeslaEvents').raiseEvent,
            raiseAlert: _status['modules'].get('TeslaEvents').raiseAlert,
            registerAlertHandler: _status['modules'].get('TeslaEvents').registerAlertHandler,
            registerEventHandler: _status['modules'].get('TeslaEvents').registerEventHandler,
            sendData: _status['modules'].get('TeslaCommunication').sendData,
            getAlerts: _status['modules'].get('TeslaEvents').getAlerts,
            clearAlerts: _status['modules'].get('TeslaEvents').clearAlerts,
            getLearner: getLearner,
            getActivity: getActivity,
            getInstruments: getInstruments,
            getSessionId: getSessionId,
            isActive: isActive,
            showAlertsModal: _status['modules'].get('TeslaAlertsModal').showAlertsModal,
        }

        // Configure registered modules
        _status['modules'].forEach(function(mod) {
            mod.configure(exported_methods, _config)
        })

        // Enable debug console detection
        /*Object.defineProperty(checkElement, 'id', {
            get: function() {
                checkStatus = 'on';
                throw new Error("Dev tools checker");
            }
        });
        requestAnimationFrame(function check() {
            checkStatus = 'off';
            console.dir(checkElement);
            checkStatusChange();
            // document.querySelector('#devtool-status').className  = checkStatus;
            requestAnimationFrame(check);
        });*/

        // Show ethical warning
        showEthicalWarning(config['allowCaptureRejection'], getInstruments(), function() {
            _status['isEthicalWarningAccepted'] = true;
            // Show TeSLA Menu
            showMenu(getInstruments(), getLogoUrl(), getDashboardUrl());
            // Start capturing
            startCapture();
        });
    }

    function configure(core, config) {

    }

    /* Register the module */
    TeslaConnector.registerModule("TeslaCore", {
        configure: configure,
        run: run
    });

	return TeslaConnector;
}(TeslaConnector || {}));
