"""Command line interface for generating OpenConf-style device configuration.

The loader supports an Ansible-style hierarchy using ``group_vars`` and
``host_vars``.  Configuration is merged in the following order:

1. ``group_vars/global`` (if present)
2. ``group_vars/<site>`` where ``site`` is defined in the host file
3. ``host_vars/<hostname>`` which only contains host specific overrides
"""

from __future__ import annotations

import argparse
import json
import os
import yaml

from .device import NetworkDevice
from .models import (
    DeviceConfig,
    Interface,
    ClockConfig,
    BgpConfig,
    BgpNeighbor,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("hostname", help="Hostname of the device")
    parser.add_argument(
        "--vars-dir",
        default="host_vars",
        help="Directory containing host variable files",
    )
    parser.add_argument(
        "--groups-dir",
        default="group_vars",
        help="Directory containing group variable files",
    )
    return parser.parse_args()


def _find_file(basename: str, directory: str) -> str | None:
    """Return the first file matching ``basename`` in ``directory``."""

    for ext in (".json", ".yaml", ".yml"):
        candidate = os.path.join(directory, basename + ext)
        if os.path.exists(candidate):
            return candidate
    return None


def _load_file(path: str) -> dict:
    with open(path, "r", encoding="utf-8") as handle:
        if path.endswith(".json"):
            return json.load(handle)
        return yaml.safe_load(handle)


def _merge(base: dict, override: dict) -> dict:
    for key, value in override.items():
        if (
            key in base
            and isinstance(base[key], dict)
            and isinstance(value, dict)
        ):
            base[key] = _merge(base[key], value)
        else:
            base[key] = value
    return base


def load_device_config(
    hostname: str,
    vars_dir: str = "host_vars",
    groups_dir: str = "group_vars",
) -> DeviceConfig:
    """Load hierarchical configuration for ``hostname``."""

    host_file = _find_file(hostname, vars_dir)
    if not host_file:
        raise FileNotFoundError(
            f"No configuration for {hostname} found in {vars_dir}"
        )

    host_data = _load_file(host_file)
    site = host_data.pop("site", None)

    final: dict = {}
    global_file = _find_file("global", groups_dir)
    if global_file:
        final = _merge(final, _load_file(global_file))

    if site:
        site_file = _find_file(site, groups_dir)
        if site_file:
            final = _merge(final, _load_file(site_file))

    final = _merge(final, host_data)

    device = DeviceConfig(hostname=hostname)
    for iface_data in final.get("interfaces", []):
        iface = Interface(**iface_data)
        device.add_interface(iface)
    clock_data = final.get("clock")
    if clock_data:
        device.clock = ClockConfig(**clock_data)
    bgp_data = final.get("bgp")
    if bgp_data:
        bgp = BgpConfig(asn=bgp_data.get("asn", 0))
        for n_data in bgp_data.get("neighbors", []):
            bgp.add_neighbor(BgpNeighbor(**n_data))
        device.bgp = bgp
    return device


def main() -> None:
    args = parse_args()
    device_config = load_device_config(
        args.hostname,
        vars_dir=args.vars_dir,
        groups_dir=args.groups_dir,
    )
    device = NetworkDevice(device_config)
    print(device.to_openconf())


if __name__ == "__main__":
    main()
