from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class ClockConfig:
    """System clock settings."""
    timezone: str = "UTC"
    ntp_servers: List[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "timezone": self.timezone,
            "ntp_servers": self.ntp_servers,
        }


@dataclass
class SystemConfig:
    """System-wide settings."""
    clock: Optional[ClockConfig] = None

    def to_dict(self) -> dict:
        return {
            "clock": self.clock.to_dict() if self.clock else None,
        }


@dataclass
class BgpNeighbor:
    """BGP neighbor configuration."""
    peer_ip: str
    remote_as: int
    description: str = ""

    def to_dict(self) -> dict:
        return {
            "peer_ip": self.peer_ip,
            "remote_as": self.remote_as,
            "description": self.description,
        }


@dataclass
class BgpConfig:
    """BGP configuration for a device."""
    asn: int
    neighbors: List[BgpNeighbor] = field(default_factory=list)

    def add_neighbor(self, neighbor: BgpNeighbor) -> None:
        self.neighbors.append(neighbor)

    def to_dict(self) -> dict:
        return {
            "asn": self.asn,
            "neighbors": [n.to_dict() for n in self.neighbors],
        }

@dataclass
class Interface:
    """Represents a simple network interface configuration."""
    name: str
    description: str = ""
    enabled: bool = True
    ip_address: Optional[str] = None
    subnet_mask: Optional[str] = None

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "description": self.description,
            "enabled": self.enabled,
            "ip_address": self.ip_address,
            "subnet_mask": self.subnet_mask,
        }

@dataclass
class DeviceConfig:
    """A collection of interfaces forming device configuration."""
    hostname: str
    interfaces: List[Interface] = field(default_factory=list)
    system: Optional[SystemConfig] = None
    bgp: Optional[BgpConfig] = None

    def add_interface(self, interface: Interface) -> None:
        self.interfaces.append(interface)

    def to_dict(self) -> dict:
        return {
            "hostname": self.hostname,
            "interfaces": [iface.to_dict() for iface in self.interfaces],
            "system": self.system.to_dict() if self.system else None,
            "bgp": self.bgp.to_dict() if self.bgp else None,
        }
