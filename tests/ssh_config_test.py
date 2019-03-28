import os
import sys
import shutil
import logging
import unittest

if sys.version_info[0] < 3:
    from StringIO import StringIO
else:
    from io import StringIO

import docopt
from contextlib2 import redirect_stdout

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from ssh_config import SSHConfig, Host, __version__
from ssh_config import cli

logging.basicConfig(level=logging.INFO)
sample = os.path.join(os.path.dirname(__file__), "sample")

new_host = Host("server2", {"ServerAliveInterval": 200, "HostName": "203.0.113.77"})

new_data = """Host server2
    HostName 203.0.113.77
    ServerAliveInterval 200
"""


class TestSSHConfig(unittest.TestCase):
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

    def test_asdict(self):
        configs = SSHConfig.load(sample)
        self.assertEqual(
            {
                "*": {"ServerAliveInterval": 40},
                "server1": {"HostName": "203.0.113.76", "ServerAliveInterval": 200},
                "server_cmd_1": {"HostName": "203.0.113.76", "Port": 2202},
                "server_cmd_2": {
                    "HostName": "203.0.113.76",
                    "Port": 22,
                    "User": "user",
                },
                "server_cmd_3": {
                    "HostName": "203.0.113.76",
                    "Port": 2202,
                    "User": "user",
                },
            },
            configs.asdict(),
        )


class TestSSHCli(unittest.TestCase):
    def tearDown(self):
        outfile = os.path.join(os.path.dirname(__file__), "sample.out")
        if os.path.exists(outfile):
            os.remove(outfile)

    def test_cli(self):
        f = StringIO()
        with redirect_stdout(f):
            try:
                cli.main(["ssh_config", "-v"])
            except SystemExit:
                pass
            output = f.getvalue().strip()
        self.assertTrue(output.startswith("ssh_config"))

    def test_ls(self):
        expect = u"""\
    Host         HostName     User   Port   IdentityFile
========================================================
*              None           None   None   None        
server1        203.0.113.76   None   None   None        
server_cmd_1   203.0.113.76   None   2202   None        
server_cmd_2   203.0.113.76   user   22     None        
server_cmd_3   203.0.113.76   user   2202   None        

"""

        f = StringIO()
        with redirect_stdout(f):
            cli.main(["ssh_config", "-f", sample, "ls"])
        output = f.getvalue()
        self.maxDiff = None
        self.assertEqual(expect, output)

    def test_ls_with_pattern(self):
        expect = u"""\
    Host         HostName     User   Port   IdentityFile
========================================================
server_cmd_1   203.0.113.76   None   2202   None        
server_cmd_2   203.0.113.76   user   22     None        
server_cmd_3   203.0.113.76   user   2202   None        

"""
        f = StringIO()
        with redirect_stdout(f):
            cli.main(["ssh_config", "-f", sample, "ls", "server_*"])
        output = f.getvalue()
        self.maxDiff = None
        self.assertEqual(expect, output)

    def test_add_error(self):
        self.assertRaises(
            docopt.DocoptExit, cli.main, ["ssh_config", "add", "test_add"]
        )

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

    def test_update_error(self):
        new_sample = os.path.join(os.path.dirname(__file__), "sample.update")
        shutil.copy(sample, new_sample)
        with self.assertRaises(docopt.DocoptExit) as e:
            cli.main(
                [
                    "ssh_config",
                    "-f",
                    new_sample,
                    "add",
                    "--update",
                    "-y",
                    "server1",
                    "IdentityFile",
                ]
            )
        self.assertTrue(
            str(e.exception).startswith(
                "<attribute=value> like options aren't provided, list index out of range"
            )
        )
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
        cli.main(["ssh_config", "-f", new_sample, "rm", "-y", "server1"])
        sshconfig = SSHConfig.load(new_sample)
        host = sshconfig.get("server1", raise_exception=False)
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

    def test_export(self):
        self.maxDiff = None
        outfile = os.path.join(os.path.dirname(__file__), "sample.out")
        cli.main(["ssh_config", "-f", sample, "export", outfile])
        with open(outfile, "r") as f:
            self.assertEqual(
                """\
Name,HostName,User,Port,IdentityFile,ProxyCommand,LocalCommand,LocalForward,Match,AddKeysToAgent,AddressFamily,BatchMode,BindAddress,BindInterface,CanonialDomains,CnonicalizeFallbackLocal,IdentityAgent,LogLevel,PreferredAuthentications,ServerAliveInterval
*,,,,,,,,,,,,,,,,,,,40
server1,203.0.113.76,,,,,,,,,,,,,,,,,,200
server_cmd_1,203.0.113.76,,2202,,,,,,,,,,,,,,,,
server_cmd_2,203.0.113.76,user,22,,,,,,,,,,,,,,,,
server_cmd_3,203.0.113.76,user,2202,,,,,,,,,,,,,,,,
""",
                f.read(),
            )
        os.remove(outfile)

        cli.main(["ssh_config", "-f", sample, "export", "csv", outfile])
        with open(outfile, "r") as f:
            self.assertEqual(
                """\
Name,HostName,User,Port,IdentityFile,ProxyCommand,LocalCommand,LocalForward,Match,AddKeysToAgent,AddressFamily,BatchMode,BindAddress,BindInterface,CanonialDomains,CnonicalizeFallbackLocal,IdentityAgent,LogLevel,PreferredAuthentications,ServerAliveInterval
*,,,,,,,,,,,,,,,,,,,40
server1,203.0.113.76,,,,,,,,,,,,,,,,,,200
server_cmd_1,203.0.113.76,,2202,,,,,,,,,,,,,,,,
server_cmd_2,203.0.113.76,user,22,,,,,,,,,,,,,,,,
server_cmd_3,203.0.113.76,user,2202,,,,,,,,,,,,,,,,
""",
                f.read(),
            )
        os.remove(outfile)
        cli.main(["ssh_config", "-f", sample, "export", "-x", "csv", outfile])
        with open(outfile, "r") as f:
            self.assertEqual(
                """\
Name,HostName,User,Port,IdentityFile
*,,,,
server1,203.0.113.76,,,
server_cmd_1,203.0.113.76,,2202,
server_cmd_2,203.0.113.76,user,22,
server_cmd_3,203.0.113.76,user,2202,
""",
                f.read(),
            )
        os.remove(outfile)
        cli.main(["ssh_config", "-f", sample, "export", "-c","HostName,User,Port,IdentityFile,ServerAliveInterval", "csv", outfile])
        with open(outfile, "r") as f:
            self.assertEqual(
                """\
Name,HostName,User,Port,IdentityFile,ServerAliveInterval
*,,,,,40
server1,203.0.113.76,,,,200
server_cmd_1,203.0.113.76,,2202,,
server_cmd_2,203.0.113.76,user,22,,
server_cmd_3,203.0.113.76,user,2202,,
""",
                f.read(),
            )
        os.remove(outfile)
        # cli.main(["ssh_config", "-f", sample, "export", "json", "sample.json"])
        # cli.main(["ssh_config", "-f", sample, "export", "ansible", "sample.yml"])


if __name__ == "__main__":
    unittest.main()
