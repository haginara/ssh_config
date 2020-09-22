#!/usr/bin/env python3

from __future__ import print_function, absolute_import
import os
import stat
import sys

from docopt import docopt
from docopt import DocoptExit

import ssh_config
from .commands import commands
from .commands.utils import input_is_yes
from .client import SSHConfig
from .version import __version__


class SSHConfigDocOpt:
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
    def __init__(self, *argv, **kwargs):
        try:
            docstring = self.__doc__.format(version=__version__)
            options = docopt(docstring, *argv, **kwargs)
        except DocoptExit:
            raise SystemExit(docstring)

        if options.get("<command>") is None:
            raise SystemExit(docstring)

        command_name = options["<command>"].title()
        command_options = options.get("<args>")
        config_path = options.get("--config")
        sshconfig = self.get_sshconfig(config_path, create=False)
        command_cls = getattr(commands, command_name)
        command = command_cls(sshconfig, command_options, options)
        command.execute()

    def get_sshconfig(self, configpath, create=True):
        sshconfig = None
        config_fullpath = os.path.expanduser(configpath)
        if os.path.exists(config_fullpath):
            try:
                sshconfig = SSHConfig.load(config_fullpath)
            except ssh_config.EmptySSHConfig:
                sshconfig = SSHConfig(config_fullpath)
        elif create:
            answer = input_is_yes(
                f"{config_fullpath} does not exists, Do you want to create new one",
                default="n",
            )
            if answer:
                open(config_fullpath, "w").close()
                os.chmod(config_fullpath, stat.S_IREAD | stat.S_IWRITE)
                print("Created!")
            sshconfig = SSHConfig(config_fullpath)
        return sshconfig


def main(argv=sys.argv):
    SSHConfigDocOpt(
        argv[1:], options_first=True, version="ssh_config %s" % __version__
    )


if __name__ == "__main__":
    main()
