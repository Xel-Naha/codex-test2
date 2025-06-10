# OpenConf Device Example

This repository demonstrates a minimal Python project for configuring
network devices using an **OpenConf-style** data structure.  It now uses
an Ansible-like directory layout with ``group_vars`` and ``host_vars``.
Each device has a JSON or YAML file inside ``host_vars``.
The command line interface reads one of these files and converts it
into OpenConf formatted JSON. Example configuration includes system clock
settings, interface addresses and a simple BGP ASN/neighbor definition.

## Requirements

* Python 3.8+
* `pyyaml`

Install the project in editable mode:

```bash
pip install -e .
```

## Usage

Place per-device variables under ``host_vars``. For example the file
``host_vars/router1.json`` contains system clock data, interface definitions
and BGP neighbors:

```json
{
  "system": {
    "clock": {
      "timezone": "UTC",
      "ntp_servers": ["192.0.2.10", "192.0.2.11"]
    }
  },
  "interfaces": [
    {
      "name": "eth0",
      "description": "Uplink",
      "enabled": true,
      "ip_address": "192.0.2.1",
      "subnet_mask": "255.255.255.0"
    },
    {
      "name": "eth1",
      "description": "LAN",
      "enabled": true,
      "ip_address": "10.0.0.1",
      "subnet_mask": "255.255.255.0"
    }
  ],
  "bgp": {
    "asn": 100,
    "neighbors": [
      {"peer_ip": "203.0.113.2", "remote_as": 200, "description": "ISP1"},
      {"peer_ip": "203.0.113.3", "remote_as": 300, "description": "ISP2"}
    ]
  }
}
```

Run the CLI to generate configuration (it looks in ``host_vars`` by default):

```bash
openconf-cli router1
```

Group variables can supply defaults for multiple hosts. A simple file
``group_vars/all.yml`` might look like:

```yaml
system:
  clock:
    timezone: UTC
    ntp_servers:
      - 192.0.2.20
```
