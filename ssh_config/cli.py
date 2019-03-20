import os
import sys
import csv
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
        update      UPdate Host configuration
        rm          Remove exist Host configuration
        import      Import Hosts from csv file to SSH Client config
        host        Get Host information
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
            if hasattr(self, "_%s" % command):
                command = "_%s" % command
            else:
                raise NoExistCommand(command, self)
            
        command_handler = getattr(self, command)
        command_docstring = inspect.getdoc(command_handler)
        command_options = docopt(command_docstring, options["ARGS"], options_first=True)

        # options, command_handler, command_options
        command_handler(options, command_options)
    
    def get_sshconfig(self, configpath, create=True):
        sshconfig = None
        config = os.path.expanduser(configpath)
        if os.path.exists(config):
            try:
                sshconfig = SSHConfig.load(config)
            except ssh_config.EmptySSHConfig as e:
                sshconfig = SSHConfig(config)
        elif create:
            answer = input(
                "%s does not exists, Do you want to create new one[y/N]" % config
            )
            if answer == "y":
                open(config, "w").close()
                print("Created!")
            sshconfig = SSHConfig(config)
        return sshconfig
           

    def ls(self, options, command_options):
        """
        List hosts.

        usage: ls [options]

        Options:
            -q --quiet      Only display Names
            -v --verbose    Verbose output
            -h --help       Show this screen
        """
        sshconfig = self.get_sshconfig(options.get("--config"), create=False)
        if sshconfig is None:
            print("No config exist: %s" % options.get("--config"))
            return

        for host in sshconfig:
            if command_options.get("--quiet"):
                print(host.name)
            elif command_options.get("--verbose"):
                print(host.name)
                for key, value in host.attributes.items():
                    print("%s %s" % (key, value))
            else:
                print("%s: %s" % (host.name, host.HostName))

    def add(self, options, command_options):
        """
        Add host.
        Usage: add [options] (HOSTNAME) (KEY=VAL...)

        Options:
            --update            If host exists, update it.
            -p --use-pattern    Use pattern to find hosts
            -f --force          Force add
            -v --verbose        Verbose Output
            -h --help           Shwo this screen
        """
        sshconfig = self.get_sshconfig(options.get("--config"))
        hostname = command_options.get("HOSTNAME")
        attrs = command_options.get("KEY=VAL", [])
        host = sshconfig.get(hostname, raise_exception=False)
        if host and command_options.get("--update"):
            sshconfig.update(hostname, {attr.split("=")[0]: attr.split("=")[1] for attr in attrs})
        elif host is None:
            host = Host(
                hostname, {attr.split("=")[0]: attr.split("=")[1] for attr in attrs}
            )
            sshconfig.append(host)
        else:
            print("%s host alread exist" % hostname)
            return

        if command_options.get("--force"):
            sshconfig.write()
        else:
            answer = input("Do you want to save it? [y/N]")
            if answer == "y":
                sshconfig.write()

    def rm(self, options, command_options):
        """
        Remove Host.
        Usage: rm [options] (HOSTNAME)

        Options:
            -v --verbose    Verbose output
            -f --force      Force remove given host
            -h --help       Show this screen
        """
        sshconfig = self.get_sshconfig(options.get("--config"), create=False)
        hostname = command_options.get("HOSTNAME")
        if not hostname or not sshconfig.get(hostname, raise_exception=False):
            print("No hostname")
            return
        sshconfig.remove(hostname)
        if command_options.get("--force"):
            sshconfig.write()
        else:
            answer = input("Do you want to remove %s? [y/N]" % hostname)
            if answer == "y":
                sshconfig.write()
    
    def _import(self, options, command_options):
        """
        Import hosts.
        Usage: import [options] (FILE)

        Options:
            -v --verbose    Verbose output
            -q --quiet      Quiet output
            -f --force      Force import hosts
            -h --help       Show this screen
        """
        sshconfig = self.get_sshconfig(options.get("--config"), create=True)
        queit = command_options.get("--quiet")
        csv_file = command_options.get("FILE")
        if not csv_file or not os.path.exists(csv_file):
            print("No FILE")
            return
        with open(csv_file) as csvfile:
            reader = csv.DictReader(csvfile)
            if 'Name' not in reader.fieldnames:
                print("No Name field")
                return
            for field in reader.fieldnames[1:]:
                if field not in [attr[0] for attr in Host.attrs]:
                    print("Unallowed attribute exist: %s" % field)
                    return
            for row in reader:
                hostname = row.pop('Name')
                host = Host(hostname, row)
                sshconfig.append(host)
                if not queit:
                    print('Import: %s, %s' %(host.name, host.HostName))

        if command_options.get("--force"):
            sshconfig.write()
        else:
            answer = input("Do you want to save it? [y/N]")
            if answer == "y":
                sshconfig.write()


def main(argv=sys.argv):
    dispatcher = DocOptDispather(
        argv[1:], options_first=True, version="ssh_config %s" % ssh_config.__version__
    )


if __name__ == "__main__":
    main()
