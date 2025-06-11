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
2. `group_vars/<site>.yml` – site specific settings (optional)
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


Example host specific file (`host_vars/router1.yml`) defines interface settings and BGP neighbors:

```yaml
site: dc1
interfaces:
  - name: eth0
    description: Uplink
    enabled: true
    ip_address: 192.0.2.1
    subnet_mask: 255.255.255.0
  - name: eth1
    description: LAN
    enabled: true
    ip_address: 10.0.0.1
    subnet_mask: 255.255.255.0
bgp:
  neighbors:
    - peer_ip: 203.0.113.2
      remote_as: 200
      description: ISP1
    - peer_ip: 203.0.113.3
      remote_as: 300
      description: ISP2
```

Generate the full configuration with:

```bash
openconf-cli router1
```

You can also render configuration in a vendor specific syntax using
the ``--vendor`` option.  Supported formats are ``Cisco.ios`` and
``Arista.eos``.  For example:

```bash
openconf-cli router1 --vendor Cisco.ios
```

Running the CLI will also write the structured configuration and the
vendor-rendered output under the `intended/` directory. The OpenConf JSON
for the device is saved to `intended/structured_config/<hostname>.json` and
the rendered configuration is written to `intended/configs/<hostname>.txt`.
Use the `--output-dir` option to change this location.

