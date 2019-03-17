import os
import sys
import logging
import unittest
logging.basicConfig(level=logging.DEBUG)
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from ssh_config import SSHConfig, Host

sample = os.path.join(os.path.dirname(__file__), 'sample')


class TestSSHConfig(unittest.TestCase):
    def test_load(self):
        configs = SSHConfig.load(sample)
        for config in configs:
            self.assertIn(config.name, ['server1', '*'])
    
    def test_other(self):
        configs = SSHConfig.load(sample)
        for config in configs:
            self.assertIn(config.name, ['server1', '*'])
    
    

if __name__ == '__main__':
    unittest.main()