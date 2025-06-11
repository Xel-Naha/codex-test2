import unittest
from openconf_device.main import load_host_config

class TestMain(unittest.TestCase):
    def test_load_host_config(self):
        cfg = load_host_config('router1', vars_dir='host_vars')
        self.assertEqual(cfg.hostname, 'router1')
        self.assertEqual(len(cfg.interfaces), 2)
        self.assertEqual(cfg.bgp.asn, 100)

    def test_load_missing_host_config(self):
        """Loading a non-existent host file should raise FileNotFoundError."""
        with self.assertRaises(FileNotFoundError):
            load_host_config('nonexistent', vars_dir='host_vars')

if __name__ == '__main__':
    unittest.main()
