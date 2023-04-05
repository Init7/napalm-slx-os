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
import socket
from typing import List, Dict, Union, Any

from napalm.base import NetworkDriver
from napalm.base.exceptions import ConnectionClosedException
from napalm.base.netmiko_helpers import netmiko_args


class SLXOSDriver(NetworkDriver):
    """Napalm driver for slx_os."""

    def __init__(self, hostname, username, password, timeout=60, optional_args=None):
        """Constructor."""
        self.device = None
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
