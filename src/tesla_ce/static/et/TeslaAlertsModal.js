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
var TeslaAlertsModal = (function (TeslaConnector) {
    let modal = document.getElementById("TeSLA_Alerts_Modal");
    let _core_module = null;

    function showAlertsModal() {
        if (modal == null) {
            modal = document.createElement('div');
            modal.id = "TeSLA_Alerts_Modal";
            modal.classList = "tesla-modal tesla-modal-top";
            modal.role = "dialog";
            modal.style = "display: none";
            let modal_html = [];
            modal_html.push('<div class="tesla-modal-dialog tesla-modal-dialog-centered" role="document">');
            modal_html.push('   <div class="tesla-modal-content">');
            modal_html.push('       <div class="tesla-modal-header">');
            modal_html.push('           Alerts');
            modal_html.push('       </div>');
            modal_html.push('       <div class="tesla-modal-body">');
            modal_html.push('           <table id="tesla_table_alerts" class="tesla-alerts-table">');
            modal_html.push('           </table>');
            modal_html.push('       </div>');
            modal_html.push('       <div class="tesla-modal-footer">');
            modal_html.push('           <button type="button" class="btn btn-secondary" id="TeSLAAlertsModalClearBtn"  data-dismiss="modal">Clear Alerts</button>');
            modal_html.push('           <button type="button" id="TeSLAAlertsModalCloseBtn" class="btn btn-primary">Close</button>');
            modal_html.push('       </div>');
            modal_html.push('   </div>');
            modal_html.push('</div>');
            modal.innerHTML = modal_html.join('\n');
            document.body.appendChild(modal);
        }

        let alerts_table = document.getElementById('tesla_table_alerts');
        let alerts_list = [];
        let alerts = _core_module.getAlerts();
        alerts_list.push('           <table id="tesla_table_alerts">');
        alerts_list.push('              <tr>');
        alerts_list.push('                  <th>Level</th>');
        alerts_list.push('                  <th>Type</th>');
        alerts_list.push('                  <th>Raised</th>');
        alerts_list.push('                  <th>Info</th>');
        alerts_list.push('              </tr>');
        for(let i=0; i<alerts.length; i++) {
            alerts_list.push('              <tr>');
            alerts_list.push('                  <td>' + alerts[i]['level'] + '</td>');
            alerts_list.push('                  <td>' + alerts[i]['info']['type'] + '</td>');
            alerts_list.push('                  <td>' + new Date(alerts[i]['raised_at']).toISOString() + '</td>');
            alerts_list.push('                  <td>' + JSON.stringify(alerts[i]['info']) + '</td>');
            alerts_list.push('              </tr>');
        }
        alerts_table.innerHTML = alerts_list.join('\n');
        openModal();
    }

    function openModal() {
        // show the modal
        modal.style.display = 'flex';

        // Trap the screen reader focus as well with aria roles. This is much easier as our main and modal elements are siblings, otherwise you'd have to set aria-hidden on every screen reader focusable element not in the modal.
        modal.removeAttribute('aria-hidden');
        // main.setAttribute('aria-hidden', 'true');

        let accept_button = document.getElementById('TeSLAAlertsModalCloseBtn');
        accept_button.onclick = function() {
            closeModal();
        }

        let reject_button = document.getElementById('TeSLAAlertsModalClearBtn');
        reject_button.onclick = function () {
            _core_module.clearAlerts();
            closeModal();
        }
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

    TeslaConnector.registerModule("TeslaAlertsModal", {
        configure: configure,
        showAlertsModal: showAlertsModal
    });

	return TeslaConnector;
}(TeslaConnector || {}));
