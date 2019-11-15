#!/usr/bin/env python3

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
import importlib
from . import commands
from .commands.utils import input_is_yes
from .client import SSHConfig, Host
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
        ls          Show list of Hosts in client file
        get         Get ssh client config with Name
        add         Add new Host configuration
        update      Update host configuration
        rm          Remove exist Host configuration
        import      Import Hosts from csv file to SSH Client config
        export      Export Hosts to csv format
        bastion     Bastion register/use
        ping        Check host is reachable
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
        if sshconfig is None:
            print(f"No config exist: {config_path}")
            return

        #command_cls = importlib.import_module(f".commands.{command_name}")
        command_cls = getattr(commands, command_name)
        command = command_cls(sshconfig, command_options, options)
        command.execute()

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


def main(argv=sys.argv):
    SSHConfigDocOpt(
        argv[1:], options_first=True, version="ssh_config %s" % __version__
    )


if __name__ == "__main__":
    main()
