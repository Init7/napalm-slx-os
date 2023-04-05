# -*- coding: utf-8 -*-
# Copyright 2016 Dravetech AB. All rights reserved.
#
# The contents of this file are licensed under the Apache License, Version 2.0
# (the "License"); you may not use this file except in compliance with the
# License. You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations under
# the License.

"""
Napalm driver for slx_os.

Read https://napalm.readthedocs.io for more information.
"""
import re
import socket
from typing import List, Dict, Union, Any, Optional

from napalm.base import NetworkDriver, models
from napalm.base.exceptions import ConnectionClosedException
from napalm.base.helpers import textfsm_extractor
from napalm.base.netmiko_helpers import netmiko_args
from netmiko import BaseConnection


class SLXOSDriver(NetworkDriver):
    """Napalm driver for slx_os."""

    def __init__(self, hostname, username, password, timeout=60, optional_args=None):
        """Constructor."""
        self.device: Optional[BaseConnection] = None
        self.hostname = hostname
        self.username = username
        self.password = password
        self.timeout = timeout

        if optional_args is None:
            optional_args = {}

        self.netmiko_optional_args = netmiko_args(optional_args)

    def open(self):
        """Open connection to device"""
        self.device = self._netmiko_open(
            device_type='extreme_slx',
            netmiko_optional_args=self.netmiko_optional_args
        )

    def close(self):
        """Close connection to device"""
        self._netmiko_close()

    def _send_command(self, command):
        """Wrapper for self.device.send.command().
        If command is a list will iterate through commands until valid command.
        """
        try:
            output = self.device.send_command(command)
            return self._send_command_postprocess(output)
        except (socket.error, EOFError) as e:
            raise ConnectionClosedException(str(e))

    @staticmethod
    def _send_command_postprocess(output):
        """
        Cleanup actions on send_command() for NAPALM getters.
        """
        return output.strip()

    def cli(self, commands: List[str], encoding: str = "text") -> Dict[str, Union[str, Dict[str, Any]]]:
        if encoding not in ("text",):
            raise NotImplementedError("%s is not a supported encoding" % encoding)

        cli_output = {}

        for command in commands:
            output = self._send_command(command)
            cli_output.setdefault(command, {})
            cli_output[command] = output

        return cli_output

    def is_alive(self) -> models.AliveDict:
        return {
            'is_alive': self.device.remote_conn.transport.is_active()
        }

    def get_facts(self) -> models.FactsDict:

        show_ver = self._send_command('show version')
        show_ver_data = textfsm_extractor(self, 'show_version', show_ver)

        uptime = self._parse_uptime(show_ver_data[0]['uptime'])

        return {
            'os_version': show_ver_data[0]['firmware_name'],
            'uptime': uptime,
            'interface_list': [],
            # TODO: Implement this
            'vendor': '',
            'serial_number': '',
            'model': '',
            'hostname': '',
            'fqdn': '',
        }

    def _parse_uptime(self, uptime_string: str) -> float:
        regexes = [
            (r'(\d+)days', 86400),
            (r'(\d+)hrs', 3600),
            (r'(\d+)mins', 60),
            (r'(\d+)secs', 1),
        ]

        uptime = 0.
        for regex, multiplier in regexes:
            match = re.search(regex, uptime_string)
            if match:
                uptime += int(match.group(1)) * multiplier

        return uptime
