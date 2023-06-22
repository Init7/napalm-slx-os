# napalm-slx_os

SLX-OS driver for [NAPALM](https://github.com/napalm-automation/napalm)

Tested with the following SLX-OS versions:

- 20.3.2e

## Function Support Overview

### Configuration Support

|                 | SLX-OS |
|:----------------|:-------|
| Config. replace | No (1) |
| Config. merge   | Yes    |
| Commit Confirm  | No     |
| Compare config  | No (2) |
| Atomic Changes  | No     |
| Rollback        | No     |

(1) - Can be implemented by copying the config via scp, replacing the startup config and reloading the system (i.e.
rebooting)

(2) - No mechanism to compare the config, the merge has been implemented by using `configure terminal`, which is
executed when calling `commit_config()`

### Getters support matrix

| Getter                    | SLX-OS |
|:--------------------------|:-------|
| get_arp_table             | ✅      |
| get_bgp_config            |        |
| get_bgp_neighbors         | ✅ (1)  |
| get_bgp_neighbors_detail  | ✅ (1)  |
| get_config                | ✅ (2)  |
| get_environment           |        |
| get_facts                 | ✅      |
| get_firewall_policies     |        |
| get_interfaces            |        |
| get_interfaces_counters   |        |
| get_interfaces_ip         |        |
| get_ipv6_neighbors_table  |        |
| get_lldp_neighbors        |        |
| get_lldp_neighbors_detail |        |
| get_mac_address_table     |        |
| get_network_instances     |        |
| get_ntp_peers             |        |
| get_ntp_servers           |        |
| get_ntp_stats             |        |
| get_optics                |        |
| get_probes_config         |        |
| get_probes_results        |        |
| get_route_to              |        |
| get_snmp_information      |        |
| get_users                 |        |
| get_vlans                 |        |
| is_alive                  | ✅      |
| ping                      |        |
| traceroute                |        |

(1) - Only default VRF supported for now

(2) - `sanitized` option not supported