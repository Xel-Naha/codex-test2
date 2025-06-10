from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, List
import json

from .models import (
    DeviceConfig,
    Interface,
    ClockConfig,
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
        self.config.clock = ClockConfig(timezone=timezone, ntp_servers=ntp)

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
