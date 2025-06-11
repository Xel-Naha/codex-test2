# OpenConf Device with Ansible

This repository demonstrates generating network device configurations using an
OpenConf-style data model and **Ansible**. Variables are organised exactly as in
an Ansible project with `group_vars` and `host_vars` directories.

Configuration is hierarchical:

1. `group_vars/all.yml` – global defaults
2. `group_vars/<site>.yml` – site specific settings (optional)
3. `host_vars/<hostname>.yml` – device specific overrides

## Requirements

* Ansible 2.12+

Install Ansible with pip if needed:

```bash
pip install ansible
```

## Usage

Define your inventory. This repo includes a simple `inventory.ini` containing a
single device named `router1`.

Host specific variables live under `host_vars/<hostname>.yml`. The example file
looks like:

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

Global defaults (applied to all devices) are placed in `group_vars/all.yml`:

```yaml
clock:
  timezone: UTC
  ntp_servers:
    - 192.0.2.10
    - 192.0.2.11
bgp:
  asn: 100
```

Run the playbook to generate configuration:

```bash
ansible-playbook -i inventory.ini generate.yml -e "vendor=Cisco.ios"
```

The playbook writes the structured OpenConf JSON to
`intended/structured_config/<hostname>.json` and vendor specific configuration
to `intended/configs/<hostname>.txt`. Use `-e vendor=Arista.eos` to render
Arista EOS syntax or omit the variable to output raw OpenConf JSON.
