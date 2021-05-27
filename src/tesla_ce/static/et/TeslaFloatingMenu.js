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
var TeslaFloatingMenu = (function (TeslaConnector) {
    let _core_module = null;
    let floating_menu = document.getElementById("TeSLA_FloatingMenu");
    let main_menu = document.getElementById("TeSLA_MainMenu");
    let menu_overlay = document.getElementById("TeSLA_MainMenu_Overlay");

    // Allow to update alerts on the first start, showing alerts generated before menu was ready
    let _first_start = true;

    let expanded = false;
    let dragged = false;
    let logo = null;
    function toggle_menu() {
        if (dragged) {
            // Avoid toggle when dragging menu
            dragged = false;
            return;
        }
        if (!expanded){
            document.getElementById("TeSLA_MainMenu_Overlay").style.display="block";
            document.getElementById("TeSLA_MainMenu").style.transform="scale(3)";
            if (logo == null) {
                document.getElementById("TeSLA_MenuToggle").style.transform = "rotate(45deg)";
            } else {
                document.getElementById("TeSLA_MenuToggle").style.transform = "scale(0.5)";
            }
            expanded = true;
        } else {
            document.getElementById("TeSLA_MainMenu_Overlay").style.display="none";
            document.getElementById("TeSLA_MainMenu").style.transform="scale(0)";
            if (logo == null) {
                document.getElementById("TeSLA_MenuToggle").style.transform = "rotate(0deg)";
            } else {
                document.getElementById("TeSLA_MenuToggle").style.transform = "scale(1)";
            }
            expanded = false;
        }
    }

    function updateMenuStatus(alerts) {
        let menu_alerts = document.getElementById('menu_alerts_option');
        let canvas = document.getElementById("TeSLA_MenuToggle");
        if (canvas === null) {
            return;
        }
        let ctx = canvas.getContext('2d');
        let img = new Image;
        img.onload = function () {
            ctx.clearRect(0,0, floating_menu.clientWidth, floating_menu.clientHeight);
            ctx.drawImage(img, 5, 5, floating_menu.clientWidth - 10, floating_menu.clientHeight - 10);
            if (alerts != null && alerts.length > 0) {
                ctx.shadowColor = '#aeaeb3';
                ctx.font="24px 'Font Awesome 5 Free'";
                ctx.fillStyle='red';
                ctx.fillText('\uf071',10,90);
            }
        };
        if (alerts != null && alerts.length > 0 ) {
            ctx.shadowColor = '#d72b2b';
            menu_alerts.innerHTML = '<span class="tesla-badge">' + alerts.length + '</span>';
        } else {
            ctx.shadowColor = '#aeaeb3';
            menu_alerts.innerHTML = '';
        }
        img.src = logo;

    }

    function showMenu(instruments, logo_url=null, dashboard_url=null) {
        logo = logo_url;


        if (menu_overlay == null) {
            menu_overlay = document.createElement('div');
            menu_overlay.id = "TeSLA_MainMenu_Overlay";
            menu_overlay.classList = "tesla-menu-overlay";
            document.body.appendChild(menu_overlay);
        }
        if (floating_menu == null) {
            floating_menu = document.createElement('div');
            floating_menu.id = "TeSLA_FloatingMenu";
            floating_menu.classList = "tesla-toggle";
            let fm_html = [];
            if (logo === null) {
                floating_menu.classList = "tesla-toggle tesla-no-logo";
                fm_html.push('<i class="tesla-icon tesla-icon-menu" id="TeSLA_MenuToggle"></i>');
            } else {
                fm_html.push('<canvas class="tesla-icon tesla-icon-menu" id="TeSLA_MenuToggle" width="100%" height="100%"></canvas>');
            }
            floating_menu.innerHTML = fm_html.join('\n');
            document.body.appendChild(floating_menu);
            floating_menu.onclick = toggle_menu;

            if (logo != null) {
                let canvas = document.getElementById("TeSLA_MenuToggle");
                let ctx = canvas.getContext('2d');
                let img = new Image;
                img.onload = function () {
                    ctx.drawImage(img, 5, 5, floating_menu.clientWidth - 10, floating_menu.clientHeight - 10);
                    if(_first_start) {
                        updateMenuStatus(_core_module.getAlerts());
                        _first_start = false;
                    }
                };
                img.src = logo;
                ctx.shadowColor = '#aeaeb3';
                ctx.shadowOffsetX = 4;
                ctx.shadowOffsetY = 2;
                ctx.shadowBlur = 2;
            }
        }
        if (main_menu == null) {
            main_menu = document.createElement('div');
            main_menu.id = "TeSLA_MainMenu";
            main_menu.classList = "tesla-menu";
            let mm_html = [];
            if (dashboard_url !== null) {
                mm_html.push('<a href="' + dashboard_url + '" target="_blank"><i class="tesla-icon tesla-icon-user"></i></a>');
            } else {
                mm_html.push('<a href="#"><i class="tesla-icon tesla-icon-user"></i></a>');
            }
            mm_html.push('<a href="#"><i id="menu_alerts_option" class="tesla-icon tesla-icon-alerts"></i></a>');

            // Webcam
            if (instruments.includes(1)) {
                mm_html.push('<a id="tesla-status-webcam" class="tesla-menu-status" href="#"><i class="tesla-icon tesla-icon-video"></i></a>');
            }
            // Keyboard
            if (instruments.includes(2)) {
                 mm_html.push('<a id="tesla-status-keyboard" class="tesla-menu-status" href="#"><i class="tesla-icon tesla-icon-keyboard"></i></a>');
            }
            // Microphone
            if (instruments.includes(3)) {
                 mm_html.push('<a id="tesla-status-microphone" class="tesla-menu-status" href="#"><i class="tesla-icon tesla-icon-microphone"></i></a>');
            }
            // Assessment attachment
            if (instruments.includes(4) || instruments.includes(5)) {
                mm_html.push('<a id="tesla-status-attachment" class="tesla-menu-status" href="#"><i class="tesla-icon tesla-icon-attachment"></i></a>');
            }

            mm_html.push('<a id="tesla-status-network" class="tesla-network-stat tesla-menu-status" href="#"><i class="tesla-icon tesla-icon-network"></i></a>');

            main_menu.innerHTML = mm_html.join('\n');
            document.body.appendChild(main_menu);
        }
        expanded = false;
        dragElement(document.getElementById("TeSLA_FloatingMenu"));
        document.getElementById("TeSLA_MainMenu").style.transform="scale(0)";
        document.getElementById("TeSLA_MenuToggle").style.transform="rotate(0deg)";
        document.getElementById("menu_alerts_option").onclick  = function() {
           _core_module.showAlertsModal();
        }
    }

    let pos1 = 0, pos2 = 0, pos3 = 0, pos4 = 0;

    function dragElement(elmnt) {
        elmnt.onmousedown = dragMouseDown;
    }

    function dragMouseDown(e) {
        e = e || window.event;
        e.preventDefault();
        // get the mouse cursor position at startup:
        pos3 = e.clientX;
        pos4 = e.clientY;
        document.onmouseup = closeDragElement;
        // call a function whenever the cursor moves:
        document.onmousemove = elementDrag;
    }

    function elementDrag(e) {
        e = e || window.event;
        e.preventDefault();
        // calculate the new cursor position:
        let w = Math.round(floating_menu.clientWidth/2.0);
        let h = Math.round(floating_menu.clientHeight/2.0);
        let x = Math.max(w, Math.min(document.documentElement.clientWidth - w, e.clientX));
        let y = Math.max(h, Math.min(document.documentElement.clientHeight - h, e.clientY));
        pos1 = pos3 - x;
        pos2 = pos4 - y;
        pos3 = x;
        pos4 = y;
        // set the element's new position:
        floating_menu.style.top = (floating_menu.offsetTop - pos2) + "px";
        floating_menu.style.left = (floating_menu.offsetLeft - pos1) + "px";

        dragged = true;
    }

    function closeDragElement() {
        // stop moving when mouse button is released:
        document.onmouseup = null;
        document.onmousemove = null;
    }

    function setSensorStatus(sensor, value) {
        let status_element = document.getElementById("tesla-status-" + sensor);
        if (status_element == null) {
            return;
        }
        switch (value) {
            case 0:
                status_element.classList = "tesla-menu-status";
                break;
            case 1:
                status_element.classList = "tesla-menu-status tesla-status-ok";
                break;
            case 2:
                status_element.classList = "tesla-menu-status tesla-status-warning";
                break;
            case 3:
                status_element.classList = "tesla-menu-status tesla-status-error";
                break;
        }
    }

    function setNetworkStatus(value) {
        let status_element = document.getElementById("tesla-status-network");
        if (status_element == null) {
            return;
        }
        switch (value) {
            case 0:
                status_element.classList = "tesla-network-stat tesla-menu-status";
                break;
            case 1:
                status_element.classList = "tesla-network-stat tesla-menu-status tesla-status-ok";
                break;
            case 2:
                status_element.classList = "tesla-network-stat tesla-menu-status tesla-status-warning";
                break;
            case 3:
                status_element.classList = "tesla-network-stat tesla-menu-status tesla-status-error";
                break;
        }
    }

    function configure(core, config) {
        _core_module = core;
        _core_module.registerAlertHandler(function(alert) {
            updateMenuStatus(_core_module.getAlerts());
        });
        _core_module.registerEventHandler(function(event) {
            if (event['type'] === 'NETWORK_SPEED_CHANGE') {
                setNetworkStatus(event['info']['status']);
            } else if (event['type'] === 'NETWORK_ERROR') {
                setNetworkStatus(3);
            } else if (event['type'] === 'SENSOR_STARTED') {
                setSensorStatus(event['info']['sensor'], 1);
            } else if (event['type'] === 'ALERTS_CLEARED') {
                updateMenuStatus(_core_module.getAlerts());
            }
        });
    }

    TeslaConnector.registerModule("TeslaFloatingMenu", {
        configure: configure,
        showMenu: showMenu,
        updateMenuStatus: updateMenuStatus
    });

	return TeslaConnector;
}(TeslaConnector || {}));
