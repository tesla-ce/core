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
    Module that deals with the Events
*/
var TeslaEvents = (function (TeslaConnector) {

    // Registered event handles
    let _event_handles = [];

    // Registered alert handles
    let _alert_handles = [];

    // Active alerts
    let _alerts = [];

    let _core_module = null;

    /*
    * Raise a new alert.
    *
    * Creates a new alert object and notify all registered handles.
    *
    * @param {string}   level  Alert level ('info', 'warning', 'alert, 'error').
    * @param {Object}   info   JSON object with all information for this alert
    * @param {boolean}  notify Whether to notify learner about this alert or not
    */
    function raiseAlert(level, info, notify=null) {
        let alert = {
            raised_at: Date.now(),
            level: level,
            info: info
        }
        if (notify == null) {
            notify = level !== 'info';
        }
        if (notify) {
            _alerts.push(alert);
        }
        onAlert(alert);
    }

    /*
    * Raise a new event.
    *
    * Creates a new event object and notify all registered handles.
    *
    * @param {string}   type   Event type.
    * @param {Object}   info   JSON object with all information for this event
    */
    function raiseEvent(type, info) {
        let event = {
            created_at: Date.now(),
            type: type,
            info: info
        }
        onEvent(event);
    }

    /*
    * Notify alert
    *
    * Notify all alert handles about a new alert
    *
    * @param {Object}   alert   JSON object with all information for the alert
    */
    function onAlert(alert) {
        for (let i=0; i<_alert_handles.length; i++) {
            _alert_handles[i](alert);
        }
    }

    /*
    * Notify event
    *
    * Notify all event handles about a new event
    *
    * @param {Object}   alert   JSON object with all information for the event
    */
    function onEvent(event) {
        for (let i=0; i<_event_handles.length; i++) {
            _event_handles[i](event);
        }
    }

    /*
    * Register event handler
    *
    * Register a new event handler.
    *
    * @param {function}  handler  A function accepting a single event parameter
    */
    function registerEventHandler(handler) {
        _event_handles.push(handler);
    }

    /*
    * Register alert handler
    *
    * Register a new alert handler.
    *
    * @param {function}  handler  A function accepting a single alert parameter
    */
    function registerAlertHandler(handler) {
        _alert_handles.push(handler);
    }

    function configure(core, config) {
        _core_module = core;
    }

    function clearAlerts() {
        _alerts = [];
        _core_module.raiseEvent('ALERTS_CLEARED', null);
    }

    function getAlerts() {
        return _alerts;
    }

    TeslaConnector.registerModule("TeslaEvents", {
        configure: configure,
        registerEventHandler: registerEventHandler,
        registerAlertHandler: registerAlertHandler,
        raiseEvent: raiseEvent,
        raiseAlert: raiseAlert,
        clearAlerts: clearAlerts,
        getAlerts: getAlerts,
    });

	return TeslaConnector;
}(TeslaConnector || {}));
