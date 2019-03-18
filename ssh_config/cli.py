import os
import sys
import abc
import argparse
from docopt import docopt
from docopt import DocoptExit
import logging
import pprint
import inspect
from functools import partial
import ssh_config
from .client import SSHConfig, Host


class NoExistCommand(Exception):
    def __init__(self, command, supercommand):
        super().__init__("No Exist Command: %s" % command)

        self.command = command
        self.supercommand = supercommand


class DocOptDispather:
    """ssh_config.

    Usage:
        ssh_config [options] [COMMAND] [ARGS...]
        
    Options:
        -h --help           Show this screen.
        -v --version        Show version.
        -f --config FILE    Specify an ssh client file [default: ~/.ssh/config]
        
    Commands:
        ls          Show list of Hosts in client file
        add         Add new Host configuration
        rm          Remove exist Host configuration
        version     Show version information
    """

    def __init__(self, *argv, **kwargs):
        try:
            options = docopt(self.__doc__, *argv, **kwargs)
        except DocoptExit:
            raise SystemExit(self.__doc__)
        command = options["COMMAND"]

        if command is None:
            raise SystemExit(self.__doc__)

        if not hasattr(self, command):
            raise NoExistCommand(command, self)
        command_handler = getattr(self, command)
        command_docstring = inspect.getdoc(command_handler)
        command_options = docopt(command_docstring, options["ARGS"], options_first=True)

        # options, command_handler, command_options
        command_handler(options, command_options)

    def ls(self, options, command_options):
        """
        List hosts.

        usage: ls [options]

        Options:
            -q --quiet      Only display Names
            -v --verbose    Verbose output
            -h --help       Show this screen
        """
        config = os.path.expanduser(options["--config"])
        if not os.path.exists(config):
            print("No config exist: %s" % config)
            return
        try:
            hosts = SSHConfig.load(config)
        except ssh_config.EmptySSHConfig as e:
            print(e)
            return

        for host in hosts:
            if command_options.get("--quiet"):
                print(host.name)
            elif command_options.get("--verbose"):
                print(host.name)
                print(host.attributes)
            else:
                print("%s: %s" % (host.name, host.HostName))

    def add(self, options, command_options):
        """
        Add host.
        Usage: add [options] (HOSTNAME) (KEY=VAL...)

        Options:
            -v --verbose    Verbose Output
            -h --help       Shwo this screen
        """
        config = os.path.expanduser(options["--config"])
        if not os.path.exists(config):
            answer = input(
                "%s does not exists, Do you want to create new one[y/N]" % config
            )
            if answer == "y":
                open(config, "w").close()
                print("Created!")

        config = SSHConfig(config)
        hostname = command_options.get("HOSTNAME")
        if not hostname:
            print("No hostname")
            return
        attrs = command_options.get("KEY=VAL", [])
        host = Host(
            hostname, {attr.split("=")[0]: attr.split("=")[1] for attr in attrs}
        )
        config.append(host)
        print("Host %s" % host.name)
        for key, value in host.attributes.items():
            print("  %s %s" % (key, value))
        answer = input("Do you want to save it? [y/N]")
        if answer == "y":
            config.write()

    def rm(self, options, command_options):
        """
        Remove Host.
        Usage: rm [options] (HOSTNAME)

        Options:
            -v --verbose    Verbose output
            -f --force      Forcely remove given host
            -h --help       Show this screen
        """
        config = os.path.expanduser(options["--config"])
        if not os.path.exists(config):
            print("No config exist: %s" % config)
            return
        try:
            sshconfig = SSHConfig.load(config)
        except ssh_config.EmptySSHConfig as e:
            print(e)
            return
        hostname = command_options.get("HOSTNAME")
        if not hostname:
            print("No hostname")
            return
        host = sshconfig.get(hostname)
        answer = input("Do you want to remove %s? [y/N]" % host.name)
        if answer == "y":
            sshconfig.remove(hostname)
            sshconfig.write()


def main(argv=sys.argv):
    dispatcher = DocOptDispather(
        argv[1:], options_first=True, version="ssh_config %s" % ssh_config.__version__
    )
    """
    options, args = parser.parse_known_args(argv[1:])
    options.config = os.path.expanduser(options.config)

    if not os.path.exists(options.config):
        answer = input(
            "%s does not exists, Do you want to create new one[y/N]" % options.config
        )
        if answer == "y":
            open(options.config, "w").close()
            print("Created!")
        else:
            return
    config = SSHConfig(options.config)
    hosts = SSHConfig.load(options.config)
    for host in hosts:
        print("Name: %s, Config: %s" % (host.name, host.attributes))
    """


if __name__ == "__main__":
    main()
