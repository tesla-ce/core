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
var TeslaSensorWebcam = (function (TeslaConnector) {

    let _core_module = null;
    let _capturing = false;
    let _capture_mode = null;
    let _video_options = {
        enabled: false,
        fps: 0.1,
        mode: 'image',
    }

    let _audio_options = {
        enabled: false,
        fragment_length: 10,
        fragment_gap: 5,
    }

    function configure(core, config) {
        _core_module = core;
        _capture_mode = config['mode'];
        if (config['instruments'].indexOf(1) >= 0) {
            _video_options['enabled'] = true;
        }
        if (config['instruments'].indexOf(3) >= 0) {
            _audio_options['enabled'] = true;
        }
    }

    function captureFrame() {
        _core_module.sendData(_capture_mode, "webcam sensor data", 'jpeg', [1]);
        if (_capturing) {
            window.setTimeout(captureFrame, Math.round(1.0/_video_options['fps'] * 1000))
        }
    }

    function captureAudioFragment() {
        _core_module.sendData(_capture_mode, "webcam sensor data", 'wav', [3]);
        if (_capturing) {
            window.setTimeout(captureAudioFragment, _audio_options['fragment_length'] * 1000)
        }
    }

    function startCapture() {
        _capturing = true;
        _core_module.raiseAlert('info', {
            'status': 'Start capturing',
            'module': 'TeslaSensorWebcam',
            'video': _video_options,
            'audio': _audio_options,
        }, false);
        if (_video_options['enabled']) {
            window.setTimeout(captureFrame, Math.round(1.0 / _video_options['fps'] * 1000));
            _core_module.raiseEvent('SENSOR_STARTED', { sensor: 'webcam', module: 'TeslaSensorWebcam'});
        }
        if (_audio_options['enabled']) {
            window.setTimeout(captureAudioFragment, _audio_options['fragment_length'] * 1000);
            _core_module.raiseEvent('SENSOR_STARTED', { sensor: 'microphone', module: 'TeslaSensorWebcam'});
        }
    }

    function stopCapture() {
        _capturing = false;
    }

    TeslaConnector.registerModule("TeslaSensorWebcam", {
        configure: configure,
        startCapture: startCapture,
        stopCapture: stopCapture,
    });

	return TeslaConnector;
}(TeslaConnector || {}));
