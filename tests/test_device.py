import unittest
import json
from openconf_device.models import DeviceConfig, Interface, ClockConfig, SystemConfig, BgpConfig, BgpNeighbor
from openconf_device.device import NetworkDevice

class TestNetworkDevice(unittest.TestCase):
    def setUp(self):
        cfg = DeviceConfig(hostname='router1')
        cfg.add_interface(Interface(name='Ethernet0', description='Uplink', ip_address='192.0.2.1', subnet_mask='255.255.255.0'))
        cfg.add_interface(Interface(name='Ethernet1', description='LAN', ip_address='10.0.0.1', subnet_mask='255.255.255.0'))
        cfg.system = SystemConfig(clock=ClockConfig(timezone='UTC', ntp_servers=['192.0.2.10', '192.0.2.11']))
        cfg.bgp = BgpConfig(asn=100, neighbors=[
            BgpNeighbor(peer_ip='203.0.113.2', remote_as=200, description='ISP1'),
            BgpNeighbor(peer_ip='203.0.113.3', remote_as=300, description='ISP2'),
        ])
        self.device = NetworkDevice(cfg)

    def test_to_openconf(self):
        data = json.loads(self.device.to_openconf())
        self.assertEqual(data['hostname'], 'router1')
        self.assertEqual(len(data['interfaces']), 2)
        self.assertEqual(data['bgp']['asn'], 100)

    def test_cisco_render(self):
        output = self.device.to_vendor('Cisco.ios')
        self.assertIn('router bgp 100', output)
        self.assertIn('ip address 192.0.2.1 255.255.255.0', output)
        self.assertIn('neighbor 203.0.113.2 remote-as 200', output)

    def test_arista_render(self):
        output = self.device.to_vendor('Arista.eos')
        self.assertIn('router bgp 100', output)
        self.assertIn('ip address 10.0.0.1/24', output)
        self.assertIn('neighbor 203.0.113.3 remote-as 300', output)

    def test_invalid_vendor(self):
        """Unsupported vendor strings should raise ValueError."""
        with self.assertRaises(ValueError):
            self.device.to_vendor('Juniper.junos')

if __name__ == '__main__':
    unittest.main()
