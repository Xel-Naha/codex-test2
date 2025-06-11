import unittest
from openconf_device.models import Interface, ClockConfig, SystemConfig, BgpNeighbor, BgpConfig, DeviceConfig

class TestModels(unittest.TestCase):
    def test_interface_dict(self):
        iface = Interface(name='eth0', description='Uplink', enabled=True,
                          ip_address='192.0.2.1', subnet_mask='255.255.255.0')
        self.assertEqual(iface.to_dict(), {
            'name': 'eth0',
            'description': 'Uplink',
            'enabled': True,
            'ip_address': '192.0.2.1',
            'subnet_mask': '255.255.255.0'
        })

    def test_device_to_dict(self):
        iface = Interface(name='eth0', ip_address='192.0.2.1', subnet_mask='255.255.255.0')
        clock = ClockConfig(timezone='UTC', ntp_servers=['192.0.2.10'])
        system = SystemConfig(clock=clock)
        neighbor = BgpNeighbor(peer_ip='203.0.113.2', remote_as=200, description='ISP1')
        bgp = BgpConfig(asn=100, neighbors=[neighbor])
        cfg = DeviceConfig(hostname='router1', interfaces=[iface], system=system, bgp=bgp)
        self.assertEqual(cfg.to_dict(), {
            'hostname': 'router1',
            'interfaces': [iface.to_dict()],
            'system': system.to_dict(),
            'bgp': bgp.to_dict()
        })

if __name__ == '__main__':
    unittest.main()
