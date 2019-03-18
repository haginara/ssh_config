import os
import sys
import logging
import unittest

logging.basicConfig(level=logging.DEBUG)
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from ssh_config import SSHConfig, Host, __version__

sample = os.path.join(os.path.dirname(__file__), "sample")

new_host = Host("server2", {"ServerAliveInterval": 200, "HostName": "203.0.113.77"})

new_data = """Host server2
    HostName 203.0.113.77
    ServerAliveInterval 200
"""


class TestSSHConfig(unittest.TestCase):
    configs = SSHConfig.load(sample)

    def test_version(self):
        self.assertEqual("0.0.2", __version__)

    def test_load(self):
        for config in self.configs:
            self.assertIn(config.name, ["server1", "*"])
            break

    def test_other(self):
        for host in self.configs:
            if host.name == "server1":
                self.assertEqual(host.HostName, "203.0.113.76")

            if host.name == "*":
                self.assertEqual(host.ServerAliveInterval, 40)

    def test_set(self):
        host_0 = self.configs[0]
        host_1 = self.configs[1]

    def test_get_host(self):
        self.assertEqual("server1", self.configs.get("server1").name)
        self.assertRaises(KeyError, self.configs.get, "NoExist")

    def test_set_host(self):
        self.configs.append(new_host)
        self.assertEqual(new_host, self.configs[-1])

    def test_write(self):
        configs = SSHConfig.load(sample)
        configs.append(new_host)
        new_sample_path = os.path.join(os.path.dirname(__file__), "sample_new")
        configs.write(filename=new_sample_path)
        new_config = SSHConfig.load(new_sample_path)
        os.remove(new_sample_path)
        self.assertEqual("server2", new_config.get("server2").name)

    def test_new(self):
        empty_sample = os.path.join(os.path.dirname(__file__), "sample_empty")
        config = SSHConfig(empty_sample)
        config.append(new_host)
        config.write()
        with open(empty_sample, "r") as f:
            self.assertEqual(new_data, f.read())
        os.remove(empty_sample)

    def test_remove(self):
        self.configs.remove("server1")
        self.assertRaises(KeyError, self.configs.get, "server1")

    def test_host_command(self):
        self.assertEqual("ssh 203.0.113.76", self.configs.get("server1").command())
        self.assertEqual(
            "ssh -P 2202 203.0.113.76", self.configs.get("server_cmd_1").command()
        )
        self.assertEqual(
            "ssh user@203.0.113.76", self.configs.get("server_cmd_2").command()
        )
        self.assertEqual(
            "ssh -P 2202 user@203.0.113.76", self.configs.get("server_cmd_3").command()
        )


if __name__ == "__main__":
    unittest.main()
