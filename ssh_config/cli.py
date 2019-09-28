from __future__ import print_function, absolute_import
import os
import sys
import csv
import abc
import argparse
import logging
import pprint
import inspect
import fnmatch
from functools import partial

from docopt import docopt
from docopt import DocoptExit
from jinja2 import Template
from texttable import Texttable

import ssh_config
from .client import SSHConfig, Host
from .version import __version__


if sys.version_info[0] < 3:
    input = raw_input


def input_is_yes(msg, default="n"):
    if default not in ["y", "n"]:
        raise Exception("Only accept 'y' or 'n'")
    if default is "n":
        msg += " [yN]? "
    else:
        msg += " [Yn]? "
    answer = input(msg)
    if len(answer) == 1 and answer[0].upper() == "Y":
        return True
    return False


class AurgmentRequired(Exception):
    pass

class NoExistCommand(Exception):
    def __init__(self, command, supercommand):
        super().__init__("No Exist Command: %s" % command)

        self.command = command
        self.supercommand = supercommand

def coroutine(func):
    def start(*args, **kwargs):
        cr = func(*args, **kwargs)
        next(cr)
        return cr
    return start

@coroutine
def grep(pattern, target):
    while True:
        host = yield
        name = host.name
        hostname = str(host.HostName)
        if pattern is None or fnmatch.fnmatch(host.name, pattern) or pattern in name or pattern in hostname:
            target.send(host)

@coroutine
def simple_print():
    while True:
        host = yield
        print(host.name)

@coroutine
def field_print(fields):
    while True:
        host = yield
        row = ",".join([getattr(host, field) for field in fields.split(",")])
        print(row)

@coroutine
def table_print(verbose=False):
    ## Print Table
    table = Texttable(max_width=100)
    table.set_deco(Texttable.HEADER)
    header = ["Host", "HostName", "User", "Port", "IdentityFile"]
    if verbose:
        table.header(header + ["Others"])
    else:
        table.header(header)

    try:
        while True:
            host = yield
            if verbose:
                others = "\n".join(
                    [
                        "%s %s" % (key, value)
                        for key, value in host.attributes(exclude=header).items()
                    ]
                )

                table.add_row(
                    [
                        host.name,
                        host.HostName,
                        host.User,
                        host.Port,
                        host.IdentityFile,
                        others,
                    ]
                )
            else:
                table.add_row(
                    [
                        host.name,
                        host.HostName,
                        host.User,
                        host.Port,
                        host.IdentityFile,
                    ]
                )
    except GeneratorExit:
        print(table.draw() + "\n")

class SSHConfigDocOpt:
    """ssh-config {version}

    Usage:
        ssh-config [options] [COMMAND] [ARGS...]
        
    Options:
        -h --help           Show this screen.
        -v --version        Show version.
        -V --verbose        Verbose output
        -f --config FILE    Specify an ssh client file [default: ~/.ssh/config]
        
    Commands:
        ls          Show list of Hosts in client file
        get         Get ssh client config with Name
        add         Add new Host configuration
        update      Update host configuration
        rm          Remove exist Host configuration
        import      Import Hosts from csv file to SSH Client config
        export      Export Hosts to csv format
        bastion     Bastion register/use
        version     Show version information
    """

    def __init__(self, *argv, **kwargs):
        try:
            docstring = self.__doc__.format(version=__version__)
            options = docopt(docstring, *argv, **kwargs)
        except DocoptExit:
            raise SystemExit(docstring)
        command = options["COMMAND"]

        if command is None:
            raise SystemExit(docstring)

        if not hasattr(self, command):
            if hasattr(self, "_%s" % command):
                command = "_%s" % command
            else:
                raise NoExistCommand(command, self)

        command_handler = getattr(self, command)
        command_docstring = inspect.getdoc(command_handler)
        template = Template(command_docstring, trim_blocks=True, lstrip_blocks=True)
        command_docstring = template.render(attrs=Host.attrs)
        command_options = docopt(command_docstring, options["ARGS"], options_first=True)

        # options, command_handler, command_options
        try:
            sshconfig = self.get_sshconfig(options.get("--config"), create=False)
            if sshconfig is None:
                print("No config exist: %s" % options.get("--config"))
                return
            command_handler(sshconfig, options, command_options)
        except Exception as e:
            raise DocoptExit(str(e))

    def get_sshconfig(self, configpath, create=True):
        sshconfig = None
        config = os.path.expanduser(configpath)
        if os.path.exists(config):
            try:
                sshconfig = SSHConfig.load(config)
            except ssh_config.EmptySSHConfig:
                sshconfig = SSHConfig(config)
        elif create:
            answer = input_is_yes(
                "%s does not exists, Do you want to create new one" % config,
                default="n",
            )
            if answer:
                open(config, "w").close()
                print("Created!")
            sshconfig = SSHConfig(config)
        return sshconfig

    def get(self, sshconfig, options, command_options):
        """
        Get hosts.
        usage: get [options] [PATTERN]

        Options:
            -h --help           Show this screen
        """
        pattern = command_options.get("PATTERN", None)
        if pattern is None:
            raise AurgmentRequired
        # Print plain
        target = grep(pattern, table_print())
        for host in sshconfig:
            target.send(host)

    def ls(self, sshconfig, options, command_options):
        """
        List hosts.
        usage: ls [options] [PATTERN]

        Options:
            --only-name             Print name only
            --fields [FIELD...]     Print selected fields, fielda are spliited by ','
            -v --verbose            Verbose output
            -h --help               Show this screen
        """
        only_name = command_options.get("--only-name")
        fields = command_options.get("--fields") 
        pattern = command_options.get("PATTERN", None)
        verbose = command_options.get("--verbose")

        if only_name:
            printer = simple_print()
        elif fields:
            printer = field_print(fields)
        else:
            printer = table_print(verbose)

        target = grep(pattern, printer)
        for host in sshconfig:
            target.send(host)

    def add(self, sshconfig, options, command_options):
        """
        Add host.
        Usage: add [options] (HOSTNAME) <attribute=value>...

        Options:
            --update            If host exists, update it.
            -b --bastion        Add attributes for Bastion host
            -p --use-pattern    Use pattern to find hosts
            -y --yes            Force answer yes
            -v --verbose        Verbose Output
            -h --help           Shwo this screen

        Attributes:
            {% for attr, attr_type in attrs %}
            {{ attr }}
            {% endfor %}
        """
        verbose = command_options.get("--verbose")
        hostname = command_options.get("HOSTNAME")
        attrs = command_options.get("<attribute=value>", [])
        is_bastion = command_options.get("--bastion")
        try:
            attrs = {
                attr.split("=")[0]: attr.split("=")[1]
                for attr in command_options.get("<attribute=value>", [])
            }
            if is_bastion:
                attrs.update({"ProxyCommand": "none", "ForwardAgent": "yes"})
        except Exception as e:
            raise Exception("<attribute=value> like options aren't provided, %s" % e)
        use_pattern = command_options.get("--use-pattern")
        if use_pattern:
            """ use-pattern is only accept update, not add """
            hosts = [host for host in sshconfig if fnmatch.fnmatch(host.name, hostname)]
            if hosts:
                for host in hosts:
                    sshconfig.update(host.name, attrs)
            else:
                print("No hosts found")
                return
        else:
            host = sshconfig.get(hostname, raise_exception=False)
            if command_options.get("--update"):
                if not host:
                    print("No host to be updated, %s" % hostname)
                if verbose:
                    print("Update attributes: %s" % attrs)
                sshconfig.update(hostname, attrs)
            else:
                if host:
                    print("%s host already exist" % hostname)
                    return
                host = Host(hostname, attrs)
                sshconfig.append(host)

        if command_options.get("--verbose"):
            print("%s" % host)
        if command_options.get("--yes") or input_is_yes(
            "Do you want to save it", default="n"
        ):
            sshconfig.write()

    def rm(self, sshconfig, options, command_options):
        """
        Remove Host.
        Usage: rm [options] (HOSTNAME)

        Options:
            -v --verbose    Verbose output
            -y --yes        Force answer yes
            -h --help       Show this screen
        """
        verbose = command_options.get("--verbose")
        hostname = command_options.get("HOSTNAME")
        host = sshconfig.get(hostname, raise_exception=False)
        if host is None:
            print("No hostname")
            return
        if verbose:
            print("%s" % host)
        sshconfig.remove(hostname)
        if command_options.get("--yes") or input_is_yes(
            "Do you want to remove %s" % hostname, default="n"
        ):
            sshconfig.write()

    def _import(self, sshconfig, options, command_options):
        """
        Import hosts.
        Usage: import [options] (FILE)

        Options:
            -v --verbose    Verbose output
            -q --quiet      Quiet output
            -y --yes        Force answer yes
            -h --help       Show this screen
        """
        queit = command_options.get("--quiet")
        csv_file = command_options.get("FILE")
        if not csv_file or not os.path.exists(csv_file):
            print("No FILE")
            return
        with open(csv_file) as csvfile:
            reader = csv.DictReader(csvfile)
            if "Name" not in reader.fieldnames:
                print("No Name field")
                return
            for field in reader.fieldnames[1:]:
                if field not in [attr[0] for attr in Host.attrs]:
                    print("Unallowed attribute exist: %s" % field)
                    return
            for row in reader:
                hostname = row.pop("Name")
                host = Host(hostname, row)
                sshconfig.append(host)
                if not queit:
                    print("Import: %s, %s" % (host.name, host.HostName))

        if command_options.get("--yes") or input_is_yes(
            "Do you want to save it", default="n"
        ):
            sshconfig.write()

    def export(self, sshconfig, options, command_options):
        """
        Export hosts.
        Usage: export [options] ([FORMAT] <file> | <file>)
        
        Options:
            -x                  Export only essential fields
            -g --group GROUP    Name of group
            -c columns          Column names, A comma separted list of field names. 
            -h --help           Show this screen
            -v --verbose        Verbose output
            -q --quiet          Quiet output
            -y --yes            Forcily yes
        
        Format:
            csv [default]
        """
        quiet = command_options.get("--quiet")
        verbose = command_options.get("--verbose")
        essential = command_options.get("-x")
        group = command_options.get("--group")
        fields = (
            command_options.get("-c").split(",") if command_options.get("-c") else []
        )
        outfile = command_options.get("<file>")
        outformat = command_options.get("FORMAT") or "csv"
        if os.path.exists(outfile):
            print("%s exists." % outfile)
            if not command_options.get("--yes") and not input_is_yes(
                "Do you want to overwrite it", default="n"
            ):
                return

        with open(outfile, "w") as f:
            if outformat == "csv":
                if essential:
                    header = ["HostName", "User", "Port", "IdentityFile"]
                elif fields:
                    header = fields
                else:
                    header = [attr for attr, attr_type in Host.attrs]

                writer = csv.DictWriter(
                    f, fieldnames=["Name"] + header, lineterminator="\n"
                )
                writer.writeheader()
                for host in sshconfig:
                    row = {"Name": host.name}
                    row.update(host.attributes(include=header))
                    writer.writerow(row)
            elif outformat == "ansible":
                """
                in INI
                jumper ansible_port=5555 ansible_host=192.0.2.50
                in YAML
                hosts:
                    jumper:
                        ansible_port: 5555
                        ansible_host: 192.0.2.50
                """
                if group:
                    f.write("[%s]\n" % group)
                for host in sshconfig:
                    if host.name == "*":
                        continue
                    line = "{:<20}ansible_host={:<20}".format(host.name, host.HostName)
                    if host.User:
                        line += "ansible_user={:<10}".format(host.User)
                    if host.IdentityFile:
                        line += "ansible_ssh_private_key_file={:<20}".format(
                            os.path.expanduser(host.IdentityFile)
                        )
                    if verbose:
                        print(line)
                    f.write("%s\n" % line)

    def bastion(self, sshconfig, options, command_options):
        """
        Manage Bastion hosts
        Usage: bastion [options] <bastion> <server>...
        
        Options:
            -h --help           Show this screen
            -v --verbose        Verbose output
            -y --yes            Forcily yes
        """
        verbose = command_options.get("--verbose")
        bastion = command_options.get("<bastion>")
        servers = command_options.get("<server>", [])

        bastion_host = sshconfig.get(bastion)
        forward_agent = bastion_host.get("ForwardAgent", None)
        if forward_agent is None or forward_agent != "yes":
            print("%s is not bastion server" % bastion)
            return

        for server in servers:
            host = sshconfig.get(server, raise_exception=False)
            if host is None:
                print("%s does not exist" % server)
                return
            if host.get("ProxyCommand", None):
                if not command_options.get("--yes") and not input_is_yes(
                    "%s has ProxyComamnd, %s" % (host, host.ProxyCommand), default="n"
                ):
                    return
            host.set("ProxyCommand", "ProxyCommand ssh -q -A bastion -W %h:%p")


def main(argv=sys.argv):
    SSHConfigDocOpt(
        argv[1:], options_first=True, version="ssh_config %s" % __version__
    )


if __name__ == "__main__":
    main()
