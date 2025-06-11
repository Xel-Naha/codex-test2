"""Command line interface for generating OpenConf-style device configuration.

This version expects Ansible-style ``host_vars`` and ``group_vars``
directories. The CLI looks up a file named ``<hostname>.json`` or
``<hostname>.yml`` inside ``host_vars`` (by default) and converts the
contents into the OpenConf data model.
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
    SystemConfig,
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
        "--vendor",
        default=None,
        help="Render configuration for a vendor (e.g. Cisco.ios, Arista.eos)",
    )
    return parser.parse_args()


def load_host_config(hostname: str, vars_dir: str = "host_vars") -> DeviceConfig:
    """Load device configuration from ``vars_dir`` for ``hostname``.

    Supports ``.json``, ``.yaml`` and ``.yml`` formats.
    """

    candidates = [
        (os.path.join(vars_dir, f"{hostname}.json"), json.load),
        (os.path.join(vars_dir, f"{hostname}.yaml"), yaml.safe_load),
        (os.path.join(vars_dir, f"{hostname}.yml"), yaml.safe_load),
    ]

    data = None
    for path, loader in candidates:
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as handle:
                data = loader(handle)
            break
    if data is None:
        raise FileNotFoundError(
            f"No configuration for {hostname} found in {vars_dir}"
        )

    device = DeviceConfig(hostname=hostname)
    for iface_data in data.get("interfaces", []):
        iface = Interface(**iface_data)
        device.add_interface(iface)

    system_data = data.get("system", {})
    clock_data = system_data.get("clock")
    if clock_data:
        device.system = SystemConfig(clock=ClockConfig(**clock_data))
    bgp_data = data.get("bgp")
    if bgp_data:
        bgp = BgpConfig(asn=bgp_data.get("asn", 0))
        for n_data in bgp_data.get("neighbors", []):
            bgp.add_neighbor(BgpNeighbor(**n_data))
        device.bgp = bgp
    return device


def main() -> None:
    args = parse_args()
    device_config = load_host_config(args.hostname, args.vars_dir)
    device = NetworkDevice(device_config)
    if args.vendor:
        print(device.to_vendor(args.vendor))
    else:
        print(device.to_openconf())


if __name__ == "__main__":
    main()
