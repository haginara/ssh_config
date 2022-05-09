#!/usr/bin/env python3

from __future__ import print_function, absolute_import
import os
import stat
import sys

import click

from ssh_config.client import Host
from .client import SSHConfig
from .version import __version__


def get_sshconfig(configpath, create=True):
    config_fullpath = os.path.expanduser(configpath)
    sshconfig = SSHConfig(config_fullpath)
    return sshconfig


@click.group()
@click.option('--path', default=os.path.expanduser("~/.ssh/config"))
@click.option('--debug/--no-debug', default=False)
@click.pass_context
def cli(ctx, path, debug):
    ctx.ensure_object(dict)
    ctx.obj['DEBUG'] = debug
    ctx.obj['path'] = path
    if os.path.exists(path):
        ctx.obj['config'] = get_sshconfig(path)
    else:
        raise SystemExit(f"SSH config does not exists, {path}")


@cli.command('attributes')
def get_attributes():
    """Print possible attributes for Host"""
    for attr, attr_type in Host.attrs:
        click.echo(f"{attr}")


@cli.command('gen')
@click.pass_context
def gen_config(ctx):
    """ Generate the ssh config"""
    config_path = ctx.obj['path']
    ssh_path = os.path.dirname(config_path)
    if not os.path.exists(config_path):
        if not os.path.exists(ssh_path):
            os.mkdir(ssh_path)
        open(config_path, "w").close()
        os.chmod(config_path, stat.S_IREAD | stat.S_IWRITE)
        print(f"Created at {config_path}")
    else:
        if click.confirm(f"Do you want to overwrite (file: {config_path})?", abort=True):
            open(config_path, "w").close()
            os.chmod(config_path, stat.S_IREAD | stat.S_IWRITE)
            print(f"Created at {config_path}")


@cli.command('ls')
@click.option("-l", is_flag=True, help="More detail")
@click.pass_context
def list_config(ctx, l):
    """Enumerate the configs"""
    config = ctx.obj['config']
    for host in config:
        if l:
            click.echo(f"{host.name:20s}{host.HostName}")
        else:
            click.echo(host.name)


@cli.command('get')
@click.argument('name')
@click.pass_context
def get_config(ctx, name):
    """Get ssh config with name"""
    config = ctx.obj['config']
    if not config.exists(name):
        click.secho(f"No host found, {name}", fg='red')
        raise SystemExit()
    selected = config.get(name)
    click.echo(selected)


@cli.command('add')
@click.argument('name')
@click.pass_context
def add_config(ctx, name):
    """Add SSH Config into config file"""
    config = ctx.obj['config']
    if config.exists(name):
        click.secho(f"{name} already exists, use `update` instead of `add`", fg='red')
        raise SystemExit
    hostname = click.prompt('HostName')
    user = click.prompt('User', default=os.getenv('USER'), show_default=True)
    port = click.prompt('Port', type=int, default=22, show_default=True)
    attrs = {
        'HostName': hostname,
        'User': user,
        'Port': port,
    }
    host = Host(name, attrs)
    config.add(host)
    click.echo(host)
    if click.confirm("Information is correct ?", abort=False):
        config.write()
        click.secho("Addded!", fg="green")


@cli.command('update')
@click.argument('name')
@click.pass_context
def update_config(ctx, name):
    config = ctx.onj['config']

    if not config.exists(name):
        click.secho(f"{name} already exists, use `update` instead of `add`", fg='red')
        raise SystemExit



@cli.command('rename')
@click.argument('name')
@click.pass_context
def rename_config(ctx, name):
    config = ctx.onj['config']


@cli.command('remove')
@click.argument('name')
@click.pass_context
def remove_config(ctx, name):
    config = ctx.onj['config']


if __name__ == '__main__':
    """ssh-config {version}

    Usage:
        ssh-config [options] <command> [<args>...]

    Options:
        -h --help           Show this screen.
        -v --version        Show version.
        -V --verbose        Verbose output
        -f --config FILE    Specify an ssh client file [default: ~/.ssh/config]

    Commands:
        gen         Generate ssh config file
        ls          Show list of Hosts in client file
        get         Get ssh client config with Name
        add         Add new Host configuration
        update      Update host configuration
        rename      Update host configuration
        rm          Remove exist Host configuration
        import      Import Hosts from csv file to SSH Client config
        export      Export Hosts to csv format
        bastion     Bastion register/use
        ping        Send ping to selected host
        version     Show version information
    """
    cli()
