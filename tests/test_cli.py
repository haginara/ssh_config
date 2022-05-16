"""SSHConfig CLI Unit Testing
"""

from click.testing import CliRunner
import os
import shutil
import sys
import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from ssh_config.version import __version__
from ssh_config import cli
from ssh_config import SSHConfig


sample = os.path.join(os.path.dirname(__file__), "sample")


def test_get_sshconfig():
    """Teste get config"""
    config = cli.get_sshconfig(sample, create=False)
    assert config.get("server_cmd_1")


def test_get_attributes():
    """Test get attributes"""
    runner = CliRunner()
    result = runner.invoke(cli.cli, ['-f', sample, 'attributes'])
    print(result)
    assert result.exit_code == 0
    assert 'HostName' in result.output


def test_interative_shell():
    """ Test interative shell"""
    assert True


def test_gen_config():
    """Test generate Config"""
    sample_new = f"{os.path.dirname(sample)}/new_config"
    runner = CliRunner()
    result = runner.invoke(cli.cli, ['-f', sample_new, 'gen'])
    assert result.exit_code == 0
    assert os.path.exists(sample_new)
    os.remove(sample_new)


def test_list_config():
    """Test list ssh hosts from conifg"""
    runner = CliRunner()
    result = runner.invoke(cli.cli,
        ['-f', sample, 'ls'])
    output = ["*", "host_1 host_2", "server1",
        "server_cmd_1", "server_cmd_2",
        "server_cmd_3"]
    print(result.output)
    assert result.exit_code == 0
    for config in output:
        assert config in result.output


def test_get_config():
    """Test get ssh host from config"""
    runner = CliRunner()
    result = runner.invoke(cli.cli,
        ['-f', sample, 'get', 'server_cmd_1'])
    output = """Host server_cmd_1
    HostName 203.0.113.76
    Port 2202

"""
    assert result.exit_code == 0
    assert result.output == output


def test_add_config():
    """Test add ssh host to config"""
    inputs = ["1.1.1.1", "jonghak.choi", "22", "", "N", "Y"]
    sample_add = f"{os.path.dirname(sample)}/sample.add"
    shutil.copy(sample, sample_add)
    runner = CliRunner()
    result = runner.invoke(cli.cli,
        ['-f', sample_add, 'add', 'test_add'], input="\n".join(inputs))
    assert result.exit_code ==0
    assert "HostName 1.1.1.1" in result.output
    os.remove(sample_add)


def test_update_config():
    """Test update ssh host to config"""
    sample_update = f"{os.path.dirname(sample)}/sample.update"
    shutil.copy(sample, sample_update)
    runner = CliRunner()
    result = runner.invoke(cli.cli,
        ['-f', sample_update, 'update', 'server_cmd_1', 'Port=2202'], input="y")
    assert result.exit_code ==0
    os.remove(sample_update)


def test_rename_config():
    """Test reanme host name from config"""
    sample_rename = f"{os.path.dirname(sample)}/sample.rename"
    shutil.copy(sample, sample_rename)
    runner = CliRunner()
    result = runner.invoke(cli.cli,
        ['-f', sample_rename, 'rename', 'server_cmd_1', 'server_cmd_rename'], input="y")
    assert result.exit_code ==0
    os.remove(sample_rename)

def test_remove_config():
    """Test remove ssh host to config"""
    sample_rm = os.path.join(os.path.dirname(sample), "sample.rm")
    shutil.copy(sample, sample_rm)
    runner = CliRunner()
    result = runner.invoke(cli.cli,
        ['-f', sample_rm, 'remove', 'server1'], input="y")
    assert result.exit_code == 0
    os.remove(sample_rm)
