SSH Config
==========
[![PyPI version](https://badge.fury.io/py/ssh-config.svg)](https://badge.fury.io/py/ssh-config)
[![Build Status](https://travis-ci.org/haginara/ssh-config.svg?branch=master)](https://travis-ci.org/haginara/ssh-config)

SSH client config file manager

Usage
-----
```
ssh_config.

    Usage:
        ssh_config.py [options] [COMMAND] [ARGS...]
        
    Options:
        -h --help           Show this screen.
        -v --version        Show version.
        -f --config FILE    Specify an ssh client file [default: ~/.ssh/config]
        
    Commands:
        ls          Show list of Hosts in client file
        add         Add new Host configuration
        rm          Remove exist Host configuration
        version     Show version information
```