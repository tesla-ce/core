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
let TeslaPluginConnector = (function () {
    // Use code comments from https://make.wordpress.org/core/handbook/best-practices/inline-documentation-standards/javascript/

    // Configuration
    let _config = JSON.parse('{{ session_data|safe }}');

    // Load status
    let _load_status = {
        css: {},
        js: {},
        callback: false,
    };

    /*
    *   Check if TeSLA is enabled for this activity
    *
    *   @return {boolean} True if TeSLA is active or False otherwise.
    */
    function isActive() {
        return _config['active']
    }

    /*
    *   Load TeSLA
    */
    function load() {
        if (!isActive()) {
            console.log('TeSLA is disabled for this activity');
            return;
        }
        console.log('TeSLA is active for this activity. Loading required modules and injecting plugin.');
        let plugin_element = document.getElementsByTagName('tesla-web-plugin');
        if (plugin_element.length === 0) {
            plugin_element = document.createElement("tesla-web-plugin");
            document.body.appendChild(plugin_element);
        } else {
            plugin_element = plugin_element[0];
        }
        plugin_element.dataset.url = _config['data_url'];

        // Load modules
        load_modules(function() {
            console.log('TeSLA modules successfully loaded');
        });
    }

    /*
    *   Callback executed once all modules have been loaded.
    */
    function is_loaded() {
        for (let i=0; i<_load_status['css'].length; i++) {
            if (_load_status['css'][i] === false) {
                return false;
            }
        }
        for (let i=0; i<_load_status['js'].length; i++) {
            if (_load_status['js'][i] === false) {
                return false;
            }
        }
        return true;
    }

    /*
    *   Load all required modules
    */
    function load_modules(callback) {
        for (let i=0; i<_config['css'].length; i++) {
            _load_status['css'][_config['css'][i]] = false;
        }
        for (let i=0; i<_config['modules'].length; i++) {
            _load_status['js'][_config['modules'][i]] = false;
        }
        for (let i=0; i<_config['css'].length; i++) {
            let link = document.createElement( "link" );
            link.href = _config['css'][i];
            link.type = "text/css";
            link.rel = "stylesheet";
            link.media = "screen,print";
            link.onload = function() {
                _load_status['css'][_config['css'][i]] = true;
                if (is_loaded() && !_load_status['callback']) {
                    _load_status['callback'] = true;
                    callback();
                }
            };
            document.getElementsByTagName( "head" )[0].appendChild( link );
        }
        for (let i=0; i<_config['modules'].length; i++) {
            let script = document.createElement("script");
            script.src = _config['modules'][i];
            script.type = "application/javascript";
            script.onload = function() {
                _load_status['js'][_config['modules'][i]] = true;
                if (is_loaded() && !_load_status['callback']) {
                    _load_status['callback'] = true;
                    callback();
                }
            };
            document.head.appendChild(script);
        }
    }

    return {
        load: load
	};
}());

// Once loaded, initialize the TeSLA Connector
window.onload = function() {
    TeslaPluginConnector.load();
};
