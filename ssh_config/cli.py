#!/usr/bin/env python3

from __future__ import print_function, absolute_import
import os
import stat
import getpass

import socket
import sys

# windows does not have termios...
try:
    import termios
    import tty

    has_termios = True
except ImportError:
    has_termios = False

import click

from ssh_config.client import Host
from .client import SSHConfig
from .version import __version__


def get_sshconfig(configpath, create=True):
    config_fullpath = os.path.expanduser(configpath)
    sshconfig = SSHConfig(config_fullpath)
    return sshconfig


def write_config(config, msg, success):
    if click.confirm(msg, abort=False):
        config.write()
        click.secho(success, fg="green")


def posix_shell(chan):
    from paramiko.py3compat import u
    import select

    oldtty = termios.tcgetattr(sys.stdin)
    try:
        tty.setraw(sys.stdin.fileno())
        tty.setcbreak(sys.stdin.fileno())
        chan.settimeout(0.0)

        while True:
            r, w, e = select.select([chan, sys.stdin], [], [])
            if chan in r:
                try:
                    x = u(chan.recv(1024))
                    if len(x) == 0:
                        break
                    sys.stdout.write(x)
                    sys.stdout.flush()
                except socket.timeout:
                    pass
            if sys.stdin in r:
                x = sys.stdin.read(1)
                if len(x) == 0:
                    break
                chan.send(x)

    finally:
        termios.tcsetattr(sys.stdin, termios.TCSADRAIN, oldtty)


@click.group()
@click.option("-f", "--path", default=os.path.expanduser("~/.ssh/config"), show_default=True)
@click.option("--debug/--no-debug", default=False)
@click.version_option(__version__)
@click.pass_context
def cli(ctx, path, debug):
    ctx.ensure_object(dict)
    ctx.obj["DEBUG"] = debug
    ctx.obj["path"] = path

    if os.path.exists(path):
        ctx.obj["config"] = get_sshconfig(path)
    else:
        if ctx.invoked_subcommand != 'gen':
            raise SystemExit(f"SSH config does not exists, {path}")


@cli.command("attributes")
def get_attributes():
    """Print possible attributes for Host"""
    for attr, attr_type in Host.attrs:
        click.echo(f"{attr}")


@cli.command("ssh")
@click.argument("name")
@click.pass_context
def interactive_shell(ctx, name):
    """Interative shell for Host"""
    config = ctx.obj["config"]
    if not config.exists(name):
        click.secho(f"{name} does not exist", fg="red")
        raise SystemExit
    host = config.get(name)
    import paramiko

    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    if host.IdentityFile:
        identity_file = os.path.expanduser(host.IdentityFile)

    port = host.Port or 22
    click.echo(f"{host.HostName}, {host.User}, {port}, {host.IdentityFile}")
    if identity_file is None:
        password = getpass.getpass(f"{host.User}@{name}'s password: ")
    else:
        password = None
    try:
        ssh.connect(
            host.HostName,
            username=host.User,
            port=port,
            password=password,
            key_filename=identity_file,
            allow_agent=True,
        )
        channel = ssh.get_transport().open_session()
        channel.get_pty()
        channel.invoke_shell()
        posix_shell(channel)
    except Exception as e:
        click.secho(f"Failed to connect to ssh, {e}", fg="red")
    ssh.close()


@cli.command("gen")
@click.pass_context
def gen_config(ctx):
    """Generate the ssh config"""
    config_path = ctx.obj["path"]
    ssh_path = os.path.dirname(config_path)
    if not os.path.exists(config_path):
        if not os.path.exists(ssh_path):
            os.mkdir(ssh_path)
        open(config_path, "w").close()
        os.chmod(config_path, stat.S_IREAD | stat.S_IWRITE)
        click.echo(f"Created at {config_path}")
    else:
        if click.confirm(
            f"Do you want to overwrite (file: {config_path})?", abort=True
        ):
            open(config_path, "w").close()
            os.chmod(config_path, stat.S_IREAD | stat.S_IWRITE)
            click.echo(f"Created at {config_path}")


@cli.command("ls")
@click.option("-l", is_flag=True, help="More detail")
@click.pass_context
def list_config(ctx, l):
    """Enumerate the configs"""
    config = ctx.obj["config"]
    for host in config:
        if l:
            click.echo(f"{host.name:20s}{host.HostName}")
        else:
            click.echo(host.name)
    return 0


@cli.command("get")
@click.argument("name")
@click.pass_context
def get_config(ctx, name):
    """Get ssh config with name"""
    config = ctx.obj["config"]
    if not config.exists(name):
        click.secho(f"No host found, {name}", fg="red")
        raise SystemExit()
    selected = config.get(name)
    click.echo(selected)
    return 0


@cli.command("add")
@click.argument("name")
@click.pass_context
def add_config(ctx, name):
    """Add SSH Config into config file"""
    config = ctx.obj["config"]
    if config.exists(name):
        click.secho(f"{name} already exists, use `update` instead of `add`", fg="red")
        raise SystemExit
    hostname = click.prompt("HostName")
    user = click.prompt("User", default=os.getenv("USER"), show_default=True)
    port = click.prompt("Port", type=int, default=22, show_default=True)
    attrs = {
        "HostName": hostname,
        "User": user,
        "Port": port,
    }
    host = Host(name, attrs)
    config.add(host)
    click.echo(host)
    write_config(config, "Information is correct ?", "Added!")


@cli.command("update")
@click.argument("name")
@click.argument("attributes", nargs=-1, metavar="<key=value>")
@click.pass_context
def update_config(ctx, name, attributes):
    """Update the ssh Host config Attribute key=value format"""
    config = ctx.obj["config"]

    if not config.exists(name):
        click.secho(f"{name} does not exist, use `update` instead of `add`", fg="red")
        raise SystemExit

    host = config.get(name)
    click.echo(host)
    click.echo("=" * 25)
    for attribute in attributes:
        try:
            key, value = attribute.split("=")
            for attr, _ in Host.attrs:
                if attr.lower() == key.lower():
                    config.update(name, {attr: value})
                    break
            else:
                raise Exception(f"No exists Attribute: {key}")
        except Exception as e:
            click.secho(f"Wrong format of attribute, {e}", fg="red")
            raise SystemExit
        click.echo(host)

    write_config(config, "Information is correct ?", "Updated!")


@cli.command("rename")
@click.argument("name")
@click.argument("new_name")
@click.pass_context
def rename_config(ctx, name, new_name):
    config = ctx.obj["config"]

    if not config.exists(name):
        click.secho(f"{name} does not exist", fg="red")
        raise SystemExit
    config.get(name).set_name(new_name)
    click.echo(config.get(new_name))
    write_config(config, "Information is correct ?", "Renamed!")


@cli.command("remove")
@click.argument("name")
@click.pass_context
def remove_config(ctx, name):
    config = ctx.obj["config"]
    if not config.exists(name):
        click.secho(f"{name} does not exist", fg="red")
        raise SystemExit
    click.echo(config.get(name))
    config.remove(name)
    write_config(config, "Do you want to remove ?", "Removed!")


def main():
    """ssh-config {version}

    Usage:
        ssh-config [options] <command> [<args>...]

    Options:
        -h --help           Show this screen.
        -v --version        Show version.
        -V --verbose        Verbose output
        -f --config FILE    Specify an ssh client file [default: ~/.ssh/config]

    Commands:
        [x] gen         Generate ssh config file
        [x] ls          Show list of Hosts in client file
        [x] get         Get ssh client config with Name
        [x] add         Add new Host configuration
        [x] update      Update host configuration
        [x] rename      Update host configuration
        [x] rm          Remove exist Host configuration
        [] import      Import Hosts from csv file to SSH Client config
        [] export      Export Hosts to csv format
        [] bastion     Bastion register/use
        [] ping        Send ping to selected host
        [-] version     Show version information
    """
    try:
        cli()
    except SystemExit as e:
        if e.code != 0:
            raise


if __name__ == "__main__":
    main()
