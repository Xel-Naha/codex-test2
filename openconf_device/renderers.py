"""Render device configuration to vendor-specific text."""

from __future__ import annotations

from .models import DeviceConfig, Interface, ClockConfig, BgpConfig, BgpNeighbor


class BaseRenderer:
    """Base class for vendor config renderers."""

    def render(self, config: DeviceConfig) -> str:  # pragma: no cover - simple
        raise NotImplementedError


class CiscoIOSRenderer(BaseRenderer):
    """Render configuration in Cisco IOS style."""

    def render(self, config: DeviceConfig) -> str:
        lines: list[str] = []
        if config.clock:
            lines.append(f"clock timezone {config.clock.timezone}")
            for ntp in config.clock.ntp_servers:
                lines.append(f"ntp server {ntp}")
            lines.append("!")
        for iface in config.interfaces:
            lines.append(f"interface {iface.name}")
            if iface.description:
                lines.append(f" description {iface.description}")
            if iface.ip_address and iface.subnet_mask:
                lines.append(
                    f" ip address {iface.ip_address} {iface.subnet_mask}"
                )
            lines.append(" no shutdown" if iface.enabled else " shutdown")
            lines.append("!")
        if config.bgp:
            lines.append(f"router bgp {config.bgp.asn}")
            for neigh in config.bgp.neighbors:
                lines.append(
                    f" neighbor {neigh.peer_ip} remote-as {neigh.remote_as}"
                )
                if neigh.description:
                    lines.append(
                        f" neighbor {neigh.peer_ip} description {neigh.description}"
                    )
            lines.append("!")
        return "\n".join(lines)


class AristaEOSRenderer(CiscoIOSRenderer):
    """Arista EOS syntax is very similar to IOS, reuse implementation."""

    pass


def get_renderer(vendor: str) -> BaseRenderer:
    key = vendor.lower()
    if key in {"cisco.ios", "ios", "cisco_ios"}:
        return CiscoIOSRenderer()
    if key in {"arista.eos", "eos", "arista_eos"}:
        return AristaEOSRenderer()
    raise ValueError(f"Unsupported vendor: {vendor}")


def render_device_config(config: DeviceConfig, vendor: str) -> str:
    renderer = get_renderer(vendor)
    return renderer.render(config)
