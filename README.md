# OpenConf Device Example

This repository demonstrates a minimal Python project for configuring
network devices using an **OpenConf-style** data structure.  The layout
mimics Ansible with `group_vars` and `host_vars`.  Configuration is
hierarchical: a global file applies to all devices, a site (or data centre)
file refines those settings and the host file only contains values that
are different for that particular device.

## Requirements

* Python 3.8+
* `pyyaml`

Install the project in editable mode:

```bash
pip install -e .
```

## Usage

The loader looks for the following files in order and merges them:

1. `group_vars/global.yml` – global defaults
2. `group_vars/<site>.yml` – site specific settings
3. `host_vars/<hostname>.yml` – device specific overrides (must include the `site` key)

Example global file:

```yaml
clock:
  timezone: UTC
  ntp_servers:
    - 192.0.2.10
    - 192.0.2.11
bgp:
  asn: 100
```

Example site file (`group_vars/dc1.yml`):

```yaml
interfaces:
  - name: eth0
    description: Uplink
    enabled: true
  - name: eth1
    description: LAN
    enabled: true
bgp:
  neighbors:
    - peer_ip: 203.0.113.2
      remote_as: 200
      description: ISP1
    - peer_ip: 203.0.113.3
      remote_as: 300
      description: ISP2
```

And a host specific file (`host_vars/router1.yml`) only contains the site
name and addresses to override:

```yaml
site: dc1
interfaces:
  - name: eth0
    ip_address: 192.0.2.1
    subnet_mask: 255.255.255.0
  - name: eth1
    ip_address: 10.0.0.1
    subnet_mask: 255.255.255.0
```

Generate the full configuration with:

```bash
openconf-cli router1
```
