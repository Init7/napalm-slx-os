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
import dataclasses
import ipaddress
import re
import socket
from collections import defaultdict
from typing import List, Dict, Union, Any, Optional

import napalm.base.helpers
from napalm.base import NetworkDriver, models
from napalm.base.exceptions import ConnectionClosedException
from napalm.base.helpers import textfsm_extractor
from napalm.base.netmiko_helpers import netmiko_args
from netmiko import BaseConnection


@dataclasses.dataclass
class _BGPNeighborDetail:
    ip_address: str
    asn: int
    description: str
    bgp_type: str
    router_id: str
    vrf: str
    state: str
    uptime_str: str
    keep_alive_time: Optional[int]
    hold_time: Optional[int]
    local_address: Optional[str]
    local_port: Optional[int]
    remote_address: Optional[str]
    remote_port: Optional[int]
    remove_private_as_str: Optional[str]
    messages_sent_open: int
    messages_sent_update: int
    messages_sent_keepalive: int
    messages_sent_notification: int
    messages_sent_refresh: int
    messages_received_open: int
    messages_received_update: int
    messages_received_keepalive: int
    messages_received_notification: int
    messages_received_refresh: int

    @property
    def is_up(self) -> bool:
        return self.state == 'ESTABLISHED'

    @property
    def vrf_name(self) -> str:
        if self.vrf == 'default-vrf':
            return 'global'
        return self.vrf

    @property
    def messages_sent_total(self) -> int:
        return (
                self.messages_sent_open
                + self.messages_sent_update
                + self.messages_sent_keepalive
                + self.messages_sent_notification
                + self.messages_sent_refresh
        )

    @property
    def messages_received_total(self) -> int:
        return (
                self.messages_received_open
                + self.messages_received_update
                + self.messages_received_keepalive
                + self.messages_received_notification
                + self.messages_received_refresh
        )

    @property
    def uptime(self) -> int:
        return _parse_uptime(self.uptime_str)

    @property
    def remove_private_as(self) -> bool:
        return self.remove_private_as_str == 'yes'


@dataclasses.dataclass
class _BGPNeighborSummary:
    address: str
    asn: int
    state: str
    uptime_str: str
    routes_accepted: int
    routes_filtered: int
    routes_sent: int
    routes_to_send: int

    @property
    def received_routes(self):
        return self.routes_accepted + self.routes_filtered


NO_SUMMARY = _BGPNeighborSummary(
    address='',
    asn=0,
    state='',
    uptime_str='',
    routes_accepted=0,
    routes_filtered=0,
    routes_sent=0,
    routes_to_send=0)


@dataclasses.dataclass
class _BGPData:
    local_router_id: str
    local_as: int
    neighbor_details: Dict[str, _BGPNeighborDetail]
    neighbor_summaries: Dict[str, _BGPNeighborSummary]


def _parse_uptime(uptime_string: str) -> int:
    regexes = [
        (r'(\d+)days', 86400),
        (r'(\d+)hrs', 3600),
        (r'(\d+)mins', 60),
        (r'(\d+)secs', 1),
    ]

    uptime = 0
    for regex, multiplier in regexes:
        match = re.search(regex, uptime_string)
        if match:
            uptime += int(match.group(1)) * multiplier

    return uptime


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

    def _send_and_parse_command(self, command: str, template: str):
        return textfsm_extractor(self, template, self._send_command(command))

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

        version_data = self._send_and_parse_command('show version', 'show_version')[0]
        chassis_data = self._send_and_parse_command('show inventory chassis', 'show_inventory_chassis')[0]

        uptime = _parse_uptime(version_data['uptime'])

        hostname = self._send_command('show running-config switch-attributes host-name')
        hostname = hostname.split('\n')[0].split(' ')[-1].strip()

        return {
            'os_version': version_data['firmware_name'],
            'uptime': float(uptime),
            'interface_list': [],
            'serial_number': chassis_data['sn'],
            'model': chassis_data['sid'],
            'hostname': hostname,
            # Couldn't find a reliable way to get these fields
            'vendor': '',
            'fqdn': '',
        }

    def _get_bgp_data(self) -> _BGPData:

        bgp_neighbors = self._send_and_parse_command('show ip bgp neighbors', 'show_ip_bgp_neighbors')
        bgp_v6_neighbors = self._send_and_parse_command('show ipv6 bgp neighbors', 'show_ipv6_bgp_neighbors')
        bgp_summary = self._send_and_parse_command('show ip bgp summary', 'show_ip_bgp_summary')
        bgp_v6_summary = self._send_and_parse_command('show ipv6 bgp summary', 'show_ipv6_bgp_summary')

        summary_base_data = bgp_summary[0]

        neighbors_list: List[_BGPNeighborDetail] = []
        for entry in bgp_neighbors + bgp_v6_neighbors:
            neighbors_list.append(_BGPNeighborDetail(
                ip_address=napalm.base.helpers.ip(entry['ipaddress']),
                asn=napalm.base.helpers.as_number(entry['asn']),
                description=entry['description'],
                bgp_type=entry['bgptype'],
                router_id=napalm.base.helpers.ip(entry['routerid']),
                vrf=entry['vrf'],
                state=entry['state'],
                uptime_str=entry['time'],
                keep_alive_time=int(entry['keepalivetime']) if entry['keepalivetime'] else 0,
                hold_time=int(entry['holdtime']) if entry['holdtime'] else 0,
                local_address=napalm.base.helpers.ip(entry['localaddress']) if entry[
                    'localaddress'] else None,
                local_port=int(entry['localport']) if entry['localport'] else None,
                remote_address=napalm.base.helpers.ip(entry['remoteaddress']) if entry[
                    'remoteaddress'] else None,
                remote_port=int(entry['remoteport']) if entry['remoteport'] else None,
                remove_private_as_str=entry['removeprivateas'],
                messages_sent_open=int(entry['msgsentopen']),
                messages_sent_update=int(entry['msgsentupdate']),
                messages_sent_keepalive=int(entry['msgsentkeepalive']),
                messages_sent_notification=int(entry['msgsentnotification']),
                messages_sent_refresh=int(entry['msgsentrefresh']),
                messages_received_open=int(entry['msgrecvopen']),
                messages_received_update=int(entry['msgrecvupdate']),
                messages_received_keepalive=int(entry['msgrecvkeepalive']),
                messages_received_notification=int(entry['msgrecvnotification']),
                messages_received_refresh=int(entry['msgrecvrefresh']),
            ))

        summary_list: List[_BGPNeighborSummary] = []
        for entry in bgp_summary + bgp_v6_summary:
            if not entry['neighboraddress'] or entry['neighboraddress'] == '':
                continue

            summary_list.append(_BGPNeighborSummary(
                address=napalm.base.helpers.ip(entry['neighboraddress']),
                asn=napalm.base.helpers.as_number(entry['asn']),
                state=entry['state'],
                uptime_str=entry['time'],
                routes_accepted=int(entry['accepted']),
                routes_filtered=int(entry['filtered']),
                routes_sent=int(entry['sent']),
                routes_to_send=int(entry['tosend']),
            ))

        neighbors_map = {}
        for entry in neighbors_list:
            neighbors_map[entry.ip_address] = entry

        summary_map = {}
        for entry in summary_list:
            summary_map[entry.address] = entry

        return _BGPData(
            local_router_id=napalm.base.helpers.ip(summary_base_data['routerid']),
            local_as=int(summary_base_data['localas']),
            neighbor_details=neighbors_map,
            neighbor_summaries=summary_map,
        )

    def get_bgp_neighbors_detail(self, neighbor_address: str = "") -> Dict[str, models.PeerDetailsDict]:

        bgp_detail = defaultdict(lambda: defaultdict(lambda: []))

        bgp_data = self._get_bgp_data()

        for key, neighbor in bgp_data.neighbor_details.items():
            summary_data = bgp_data.neighbor_summaries[
                neighbor.ip_address] if neighbor.ip_address in bgp_data.neighbor_summaries else NO_SUMMARY

            details: models.PeerDetailsDict = {
                'up': neighbor.is_up,
                'local_as': bgp_data.local_as,
                'remote_as': neighbor.asn,
                'router_id': neighbor.router_id,
                'local_address': neighbor.local_address or '',
                'local_address_configured': False,
                'local_port': neighbor.local_port or 0,
                'routing_table': neighbor.vrf_name,
                'remote_address': neighbor.ip_address,
                'remote_port': neighbor.remote_port or 0,
                'multihop': False,
                'multipath': False,
                'remove_private_as': neighbor.remove_private_as,
                # TODO: Need more information for this
                'import_policy': '',
                'export_policy': '',
                'input_messages': neighbor.messages_received_total,
                'output_messages': neighbor.messages_sent_total,
                'input_updates': neighbor.messages_received_update,
                'output_updates': neighbor.messages_sent_update,
                'messages_queued_out': 0,
                # TODO is there a standard convention here? SLX-OS returns everything in uppercase
                'connection_state': neighbor.state,
                'previous_connection_state': '',
                'last_event': '',
                # TODO: Perhaps this is "Peer configured for AS4  capability"
                'suppress_4byte_as': False,
                'local_as_prepend': False,
                'holdtime': neighbor.hold_time or 0,
                'configured_holdtime': 0,
                'keepalive': neighbor.keep_alive_time or 0,
                'configured_keepalive': 0,
                'active_prefix_count': 0,
                'received_prefix_count': summary_data.received_routes,
                'accepted_prefix_count': summary_data.routes_accepted,
                'suppressed_prefix_count': 0,
                'advertised_prefix_count': summary_data.routes_sent,
                'flap_count': 0,
            }

            bgp_detail[neighbor.vrf_name][neighbor.asn].append(details)

        return bgp_detail

    def get_bgp_neighbors(self) -> Dict[str, models.BGPStateNeighborsPerVRFDict]:
        bgp_data = self._get_bgp_data()

        output = defaultdict(lambda: {"peers": {}})

        # TODO: Fix multi-vrf setup
        output['global']['router_id'] = bgp_data.local_router_id

        for neighbor in bgp_data.neighbor_details.values():
            summary_data = bgp_data.neighbor_summaries[
                neighbor.ip_address] if neighbor.ip_address in bgp_data.neighbor_summaries else NO_SUMMARY

            ip = ipaddress.ip_address(neighbor.ip_address)
            if ip.version == 4:
                address_family = "ipv4"
            else:
                address_family = "ipv6"

            output[neighbor.vrf_name]["peers"][neighbor.ip_address] = {
                "local_as": bgp_data.local_as,
                "remote_as": neighbor.asn,
                "remote_id": neighbor.router_id,
                "is_up": neighbor.is_up,
                "is_enabled": True,
                "description": neighbor.description,
                "uptime": neighbor.uptime,
                "address_family": {
                    address_family: {
                        "received_prefixes": summary_data.received_routes,
                        "accepted_prefixes": summary_data.routes_accepted,
                        "sent_prefixes": summary_data.routes_sent,
                    }
                }
            }

        return output
