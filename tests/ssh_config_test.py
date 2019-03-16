import os
import sys
import unittest
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from ssh_config import SSHConfig


class TestSSHConfig(unittest.TestCase):
    sample = os.path.join(
                os.path.dirname(__file__),
                'sample')
    
    def test_load(self):
        configs = SSHConfig.load(self.sample)
        for config in configs:
            print(config.host, config.config)
            self.assertIn(config.host, ['server1', '*'])


if __name__ == '__main__':
    unittest.main()