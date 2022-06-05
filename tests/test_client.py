import os
import sys
import shutil
import logging
import unittest
from unittest import mock
import pytest
from io import StringIO

from contextlib import redirect_stdout

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from ssh_config import SSHConfig, Host
from ssh_config.errors import EmptySSHConfig, WrongSSHConfig, HostExistsError

logging.basicConfig(level=logging.INFO)
sample = os.path.join(os.path.dirname(__file__), "sample")

new_host = Host("server2", {"ServerAliveInterval": 200, "HostName": "203.0.113.77"})

new_data = """Host server2
    HostName 203.0.113.77
    ServerAliveInterval 200
"""


class TestSSHConfig(unittest.TestCase):
    def test_load(self):
        configs = SSHConfig(sample)
        for config in configs:
            self.assertIn(config.name, ["server1", "*"])
            break

    def test_other(self):
        configs = SSHConfig(sample)
        for host in configs:
            if host.name == "server1":
                self.assertEqual(host.HostName, "203.0.113.76")

            if host.name == "*":
                self.assertEqual(host.ServerAliveInterval, 40)

    def test_set(self):
        configs = SSHConfig(sample)
        host_0 = configs.hosts[0]
        host_1 = configs.hosts[1]
        self.assertTrue(isinstance(host_0, Host))
        self.assertTrue(isinstance(host_1, Host))

    def test_get_host(self):
        configs = SSHConfig(sample)
        self.assertEqual("server1", configs.get("server1").name)
        with self.assertRaises(NameError):
            configs.get("NoExist")

    def test_set_host(self):
        configs = SSHConfig(sample)
        configs.add(new_host)
        self.assertEqual(new_host, configs.hosts[-1])

    def test_update(self):
        configs = SSHConfig(sample)
        configs.update("server1", {"IdentityFile": "~/.ssh/id_rsa_new"})
        self.assertRaises(AttributeError, configs.update, "server1", [])
        self.assertEqual(configs.get("server1").IdentityFile, "~/.ssh/id_rsa_new")

        attrs = {
            "HostName": "example.com",
            "User": "test",
            "Port": 22,
            "IdentityFile": "~/.ssh/id_rsa",
            "ServerAliveInterval": 10,
        }
        configs.update("server1", attrs)
        for key, value in attrs.items():
            self.assertEqual(
                getattr(configs.get("server1"), key),
                value
            )

    def test_write(self):
        configs = SSHConfig(sample)
        configs.add(new_host)
        new_sample_path = os.path.join(os.path.dirname(__file__), "sample_new")
        configs.write(filename=new_sample_path)
        new_config = SSHConfig(new_sample_path)
        os.remove(new_sample_path)
        self.assertEqual("server2", new_config.get("server2").name)

    def test_new(self):
        empty_sample = os.path.join(os.path.dirname(__file__), "sample_empty")
        config = SSHConfig.create(empty_sample)
        config.add(new_host)
        config.write()
        with open(empty_sample, "r") as f:
            self.assertEqual(new_data, f.read())
        os.remove(empty_sample)

    def test_remove(self):
        config = SSHConfig(sample)
        config.remove("server1")
        with self.assertRaises(NameError):
            config.get("server1")

    def test_host_command(self):
        configs = SSHConfig(sample)
        self.assertEqual("ssh 203.0.113.76", configs.get("server1").command())
        self.assertEqual(
            "ssh -p 2202 203.0.113.76", configs.get("server_cmd_1").command()
        )
        self.assertEqual("ssh user@203.0.113.76", configs.get("server_cmd_2").command())
        self.assertEqual(
            "ssh -p 2202 user@203.0.113.76", configs.get("server_cmd_3").command()
        )

    def test_asdict(self):
        configs = SSHConfig(sample)
        expected = sorted([
                {"Host": "*", "ServerAliveInterval": 40},
                {"Host": "server1", "HostName": "203.0.113.76", "ServerAliveInterval": 200},
                {"Host": "server_cmd_1", "HostName": "203.0.113.76", "Port": 2202},
                {"Host": "server_cmd_2", 
                    "HostName": "203.0.113.76",
                    "Port": 22,
                    "User": "user",
                },
                {"Host": "server_cmd_3", 
                    "HostName": "203.0.113.76",
                    "Port": 2202,
                    "User": "user",
                },
                {"Host": "host_1 host_2", 
                    "HostName": "%h.test.com",
                    "Port": 2202,
                    "User": "user",
                },
            ], key=lambda h: h['Host'])

        self.assertEqual(
            expected,
            sorted(configs.asdict(), key=lambda h: h['Host']),
        )


if __name__ == "__main__":
    unittest.main()
