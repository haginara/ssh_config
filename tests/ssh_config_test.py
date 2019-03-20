import os
import sys
import shutil
import logging
import unittest

logging.basicConfig(level=logging.INFO)
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from ssh_config import SSHConfig, Host, __version__
from ssh_config import cli

sample = os.path.join(os.path.dirname(__file__), "sample")

new_host = Host("server2", {"ServerAliveInterval": 200, "HostName": "203.0.113.77"})

new_data = """Host server2
    HostName 203.0.113.77
    ServerAliveInterval 200
"""


class TestSSHConfig(unittest.TestCase):
    def test_version(self):
        self.assertEqual("0.0.6", __version__)

    def test_load(self):
        configs = SSHConfig.load(sample)
        for config in configs:
            self.assertIn(config.name, ["server1", "*"])
            break

    def test_other(self):
        configs = SSHConfig.load(sample)
        for host in configs:
            if host.name == "server1":
                self.assertEqual(host.HostName, "203.0.113.76")

            if host.name == "*":
                self.assertEqual(host.ServerAliveInterval, 40)

    def test_set(self):
        configs = SSHConfig.load(sample)
        host_0 = configs[0]
        host_1 = configs[1]

    def test_get_host(self):
        configs = SSHConfig.load(sample)
        self.assertEqual("server1", configs.get("server1").name)
        self.assertRaises(KeyError, configs.get, "NoExist")

    def test_set_host(self):
        configs = SSHConfig.load(sample)
        configs.append(new_host)
        self.assertEqual(new_host, configs[-1])

    def test_update(self):
        configs = SSHConfig.load(sample)
        configs.update("server1", {"IdentityFile": "~/.ssh/id_rsa_new"})
        self.assertRaises(AttributeError, configs.update, "server1", [])
        self.assertEqual(configs.get("server1").IdentityFile, "~/.ssh/id_rsa_new")

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
        configs = SSHConfig.load(sample)
        configs.remove("server1")
        self.assertRaises(KeyError, configs.get, "server1")

    def test_host_command(self):
        configs = SSHConfig.load(sample)
        self.assertEqual("ssh 203.0.113.76", configs.get("server1").command())
        self.assertEqual(
            "ssh -p 2202 203.0.113.76", configs.get("server_cmd_1").command()
        )
        self.assertEqual("ssh user@203.0.113.76", configs.get("server_cmd_2").command())
        self.assertEqual(
            "ssh -p 2202 user@203.0.113.76", configs.get("server_cmd_3").command()
        )


if sys.version_info[0] < 3:
    from StringIO import StringIO
else:
    from io import StringIO

from contextlib2 import redirect_stdout


class TestSSHCli(unittest.TestCase):
    def test_cli(self):
        f = StringIO()
        with redirect_stdout(f):
            try:
                cli.main(["ssh_config", "-v"])
            except SystemExit:
                pass
            output = f.getvalue().strip()
        self.assertEqual("ssh_config 0.0.6", output)

    def test_ls(self):
        expect = [
            "server1: 203.0.113.76",
            "*: None",
            "server_cmd_1: 203.0.113.76",
            "server_cmd_2: 203.0.113.76",
            "server_cmd_3: 203.0.113.76",
        ]
        f = StringIO()
        with redirect_stdout(f):
            cli.main(["ssh_config", "-f", sample, "ls"])
        output = f.getvalue()
        for line in output.split("\n"):
            if line:
                self.assertIn(line, expect)

    def test_ls_with_pattern(self):
        expect = [
            "server_cmd_1: 203.0.113.76",
            "server_cmd_2: 203.0.113.76",
            "server_cmd_3: 203.0.113.76",
        ]
        f = StringIO()
        with redirect_stdout(f):
            cli.main(["ssh_config", "-f", sample, "ls", "server_*"])
        output = f.getvalue()
        for line in output.split("\n"):
            if line:
                self.assertIn(line, expect)

    def test_add(self):
        sample_add = os.path.join(os.path.dirname(__file__), "sample.add")
        shutil.copy(sample, sample_add)
        cli.main(
            [
                "ssh_config",
                "-f",
                sample_add,
                "add",
                "-y",
                "test_add",
                "HostName=238.0.4.1",
            ]
        )
        sshconfig = SSHConfig.load(sample_add)
        host = sshconfig.get("test_add", raise_exception=False)
        self.assertIsNotNone(host)
        self.assertEqual(host.HostName, "238.0.4.1")
        os.remove(sample_add)

    def test_update(self):
        new_sample = os.path.join(os.path.dirname(__file__), "sample.update")
        shutil.copy(sample, new_sample)
        cli.main(
            [
                "ssh_config",
                "-f",
                new_sample,
                "add",
                "--update",
                "-y",
                "server1",
                "IdentityFile=~/.ssh/id_rsa_test",
            ]
        )
        sshconfig = SSHConfig.load(new_sample)
        host = sshconfig.get("server1", raise_exception=False)
        self.assertEqual("203.0.113.76", host.HostName)
        self.assertEqual("~/.ssh/id_rsa_test", host.IdentityFile)
        os.remove(new_sample)

    def test_update_with_pattern(self):
        new_sample = os.path.join(os.path.dirname(__file__), "sample.update")
        shutil.copy(sample, new_sample)
        cli.main(
            [
                "ssh_config",
                "-f",
                new_sample,
                "add",
                "-y",
                "-p",
                "server_*",
                "IdentityFile=~/.ssh/id_rsa_test",
            ]
        )
        sshconfig = SSHConfig.load(new_sample)
        for host in sshconfig:
            if "server_cmd" in host.name:
                self.assertEqual("203.0.113.76", host.HostName)
                self.assertEqual("~/.ssh/id_rsa_test", host.IdentityFile)
        os.remove(new_sample)

    def test_rm(self):
        new_sample = os.path.join(os.path.dirname(__file__), "sample.rm")
        shutil.copy(sample, new_sample)
        cli.main(["ssh_config", "-f", new_sample, "rm", "-y", "test_add"])
        sshconfig = SSHConfig.load(new_sample)
        host = sshconfig.get("test_add", raise_exception=False)
        self.assertIsNone(host)
        os.remove(new_sample)

    def test_import(self):
        new_sample = os.path.join(os.path.dirname(__file__), "sample.import")
        shutil.copy(sample, new_sample)
        import_csv = os.path.join(os.path.dirname(__file__), "import.csv")
        cli.main(["ssh_config", "-f", new_sample, "import", "-q", "-y", import_csv])
        sshconfig = SSHConfig.load(new_sample)
        import_1 = sshconfig.remove("import1")
        import_2 = sshconfig.remove("import2")
        sshconfig.write()
        self.assertTrue(import_1)
        self.assertTrue(import_2)
        os.remove(new_sample)


if __name__ == "__main__":
    unittest.main()
