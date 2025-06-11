from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, List
import json

from .models import (
    DeviceConfig,
    Interface,
    ClockConfig,
    SystemConfig,
    BgpConfig,
    BgpNeighbor,
)

@dataclass
class NetworkDevice:
    """Represents a network device using an OpenConf-style configuration."""
    config: DeviceConfig

    def add_interface(
        self,
        name: str,
        description: str = "",
        enabled: bool = True,
        ip_address: Optional[str] = None,
        subnet_mask: Optional[str] = None,
    ) -> None:
        iface = Interface(
            name=name,
            description=description,
            enabled=enabled,
            ip_address=ip_address,
            subnet_mask=subnet_mask,
        )
        self.config.add_interface(iface)

    def set_clock(self, timezone: str, ntp_servers: Optional[List[str]] = None) -> None:
        """Configure system clock."""
        ntp = ntp_servers or []
        if self.config.system is None:
            self.config.system = SystemConfig()
        self.config.system.clock = ClockConfig(timezone=timezone, ntp_servers=ntp)

    def set_bgp(self, asn: int, neighbors: Optional[List[BgpNeighbor]] = None) -> None:
        """Set BGP ASN and optional neighbors."""
        self.config.bgp = BgpConfig(asn=asn)
        if neighbors:
            for n in neighbors:
                self.config.bgp.add_neighbor(n)

    def add_bgp_neighbor(self, peer_ip: str, remote_as: int, description: str = "") -> None:
        """Add a BGP neighbor."""
        if self.config.bgp is None:
            self.config.bgp = BgpConfig(asn=0)
        self.config.bgp.add_neighbor(BgpNeighbor(peer_ip=peer_ip, remote_as=remote_as, description=description))

    def to_openconf(self) -> str:
        """Return configuration encoded as JSON."""
        return json.dumps(self.config.to_dict(), indent=2)

    # New vendor rendering functionality
    def to_vendor(self, vendor: str) -> str:
        """Render configuration for a specific vendor."""
        key = vendor.lower()
        if key in {"cisco.ios", "cisco", "ios"}:
            return self._render_cisco_ios()
        if key in {"arista.eos", "arista", "eos"}:
            return self._render_arista_eos()
        raise ValueError(f"Unsupported vendor {vendor}")

    # Helper rendering methods
    def _render_cisco_ios(self) -> str:
        lines = [f"hostname {self.config.hostname}"]
        if self.config.system and self.config.system.clock:
            clock = self.config.system.clock
            lines.append(f"clock timezone {clock.timezone} 0")
            for ntp in clock.ntp_servers:
                lines.append(f"ntp server {ntp}")
        for iface in self.config.interfaces:
            lines.append(f"interface {iface.name}")
            if iface.description:
                lines.append(f" description {iface.description}")
            if iface.ip_address and iface.subnet_mask:
                lines.append(
                    f" ip address {iface.ip_address} {iface.subnet_mask}"
                )
            lines.append(" no shutdown" if iface.enabled else " shutdown")
            lines.append("!")
        if self.config.bgp:
            lines.append(f"router bgp {self.config.bgp.asn}")
            for n in self.config.bgp.neighbors:
                lines.append(f" neighbor {n.peer_ip} remote-as {n.remote_as}")
                if n.description:
                    lines.append(
                        f" neighbor {n.peer_ip} description {n.description}"
                    )
            lines.append("!")
        return "\n".join(lines)

    def _render_arista_eos(self) -> str:
        lines = [f"hostname {self.config.hostname}"]
        if self.config.system and self.config.system.clock:
            clock = self.config.system.clock
            lines.append(f"clock timezone {clock.timezone}")
            for ntp in clock.ntp_servers:
                lines.append(f"ntp server {ntp}")
        for iface in self.config.interfaces:
            lines.append(f"interface {iface.name}")
            if iface.description:
                lines.append(f" description {iface.description}")
            if iface.ip_address and iface.subnet_mask:
                # Convert subnet mask to prefix length
                prefix = sum(bin(int(x)).count("1") for x in iface.subnet_mask.split("."))
                lines.append(f" ip address {iface.ip_address}/{prefix}")
            lines.append(" no shutdown" if iface.enabled else " shutdown")
            lines.append("!")
        if self.config.bgp:
            lines.append(f"router bgp {self.config.bgp.asn}")
            for n in self.config.bgp.neighbors:
                lines.append(f" neighbor {n.peer_ip} remote-as {n.remote_as}")
                if n.description:
                    lines.append(f"  description {n.description}")
            lines.append("!")
        return "\n".join(lines)
