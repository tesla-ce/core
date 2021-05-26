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
var TeslaEthicalWarning = (function (TeslaConnector) {
    let modal = document.getElementById("TeSLA_Ethical_Modal");
    let _normal_close = false;
    let _core_module = null;

    // Create an observer instance linked to the callback function
    const observer = new MutationObserver(function(mutationsList, observer) {
        // Check if the modal has been removed
        if (document.getElementById("TeSLA_Ethical_Modal") == null) {
            for (let i=0; i<mutationsList.length; i++) {
                if (mutationsList[i].removedNodes.length > 0) {
                    for (let j=0; j<mutationsList[i].removedNodes.length; j++) {
                        if (mutationsList[i].removedNodes[j].id === "TeSLA_Ethical_Modal") {
                            document.body.appendChild(mutationsList[i].removedNodes[j])
                            _core_module.raiseAlert('alert', {
                                type: 'DOM_CHANGE',
                                message: "Detected manual removal of EthicalWarning"
                            });
                        }
                    }
                }
            }
        } else {
            for (let i=0; i<mutationsList.length; i++) {
                if (mutationsList[i].attributeName === 'style' && mutationsList[i].target.id === "TeSLA_Ethical_Modal" ){
                    if (modal.style.display !== 'flex') {
                        modal.style.display = 'flex';
                        _core_module.raiseAlert('alert', {
                            type: 'DOM_CHANGE',
                            message: "Detected manual style change of EthicalWarning"
                        });
                    }
                }
            }
        }
    });

    function showEthicalWarning(allowReject, instruments, resolve, reject) {
        if (modal == null) {
            modal = document.createElement('div');
            modal.id = "TeSLA_Ethical_Modal";
            modal.classList = "tesla-modal";
            modal.role = "dialog";
            modal.style = "display: none";
            let modal_html = [];
            modal_html.push('<div class="tesla-modal-dialog tesla-modal-dialog-centered" role="document">');
            modal_html.push('   <div class="tesla-modal-content">');
            modal_html.push('       <div class="tesla-modal-header">');
            modal_html.push('           Ethical Warning');
            modal_html.push('       </div>');
            modal_html.push('       <div class="tesla-modal-body">');
            modal_html.push('           <p class="tesla-message tesla-message-ethicwarning">');
            modal_html.push('               This assessment activity has TeSLA active. Once the activity starts, the following devices will be controlled.');
            modal_html.push('           </p>');
            modal_html.push('           <ul>');
            // Webcam
            if (instruments.includes(1)) {
                modal_html.push('<li><a href="#"><i class="tesla-icon tesla-icon-video" title="Webcam"></i></a></li>');
            }
            // Keyboard
            if (instruments.includes(2)) {
                 modal_html.push('<li><a href="#"><i class="tesla-icon tesla-icon-keyboard" title="Keyboard"></i></a></li>');
            }
            // Microphone
            if (instruments.includes(3)) {
                 modal_html.push('<li><a href="#"><i class="tesla-icon tesla-icon-microphone" title="Microphone"></i></a></li>');
            }
            // Assessment attachment
            if (instruments.includes(4) || instruments.includes(5)) {
                modal_html.push('<li><a href="#"><i class="tesla-icon tesla-icon-attachment" title="Attached documents"></i></a></li>');
            }
            modal_html.push('           </ul>');
            modal_html.push('       </div>');
            modal_html.push('       <div class="tesla-modal-footer">');
            if  (allowReject) {
                modal_html.push('           <button type="button" class="btn btn-secondary" id="TeSLAModalRejectBtn"  data-dismiss="modal">Reject</button>');
            }
            modal_html.push('           <button type="button" id="TeSLAModalAcceptBtn" class="btn btn-primary">Accept</button>');
            modal_html.push('       </div>');
            modal_html.push('   </div>');
            modal_html.push('</div>');
            modal.innerHTML = modal_html.join('\n');
            document.body.appendChild(modal);
        }

        // Start observing the target node for configured mutations
        observer.observe(document.body, {childList: true, attributes: true, subtree: true});

        return openModal(resolve, reject);
    }

    function openModal(resolve, reject) {
        _normal_close = false;
        // show the modal
        modal.style.display = 'flex';

        // Trap the screen reader focus as well with aria roles. This is much easier as our main and modal elements are siblings, otherwise you'd have to set aria-hidden on every screen reader focusable element not in the modal.
        modal.removeAttribute('aria-hidden');
        // main.setAttribute('aria-hidden', 'true');

        return new Promise(function () {
            let accept_button = document.getElementById('TeSLAModalAcceptBtn');
            accept_button.onclick = function() {
                _normal_close = true;
                observer.disconnect();
                _core_module.raiseAlert('info', {
                    type: 'ETHIC_ACCEPT',
                    message: "Ethical Warning accepted by learner"
                });
                closeModal();
                resolve();
            };

            let reject_button = document.getElementById('TeSLAModalRejectBtn');
            if (reject_button != null) {
                reject_button.onclick = function () {
                    _normal_close = true;
                    observer.disconnect();
                    _core_module.raiseAlert('alert', {
                        type: 'ETHIC_REJECTED',
                        message: "Ethical Warning rejected by learner"
                    });
                    closeModal();
                    reject();
                }
            }
        });
    }

    function closeModal(e) {
        // hide the modal
        modal.style.display = 'none';

        // Untrap screen reader focus
        modal.setAttribute('aria-hidden', 'true');
    }

    function configure(core, config) {
        _core_module = core;
    }

    TeslaConnector.registerModule("TeslaEthicalWarning", {
        configure: configure,
        showEthicalWarning: showEthicalWarning
    });

	return TeslaConnector;
}(TeslaConnector || {}));
