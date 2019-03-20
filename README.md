SSH Config
==========
[![PyPI version](https://badge.fury.io/py/ssh-config.svg)](https://badge.fury.io/py/ssh-config)
[![Build Status](https://travis-ci.org/haginara/ssh-config.svg?branch=master)](https://travis-ci.org/haginara/ssh-config)

SSH client config file manager

Why
---
I don't remember all the servers I am managing. Also all servers requires all different configuration to connec to it. I know ~.ssh/config can handle this kind of issue. I want it to handle this file easier.

Yes, I am not sure this is eaiser way to handle it. but I am trying.

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
        import      Import Hosts from csv file to SSH Client config
        version     Show version information
```

Use-cases
---------

# Want to get list of hosts in client file
```
$ ssh_config ls 
# It shows name and HostName attribute
server1: 203.0.113.76
*: None
server_cmd_1: 203.0.113.76
server_cmd_2: 203.0.113.76
server_cmd_3: 203.0.113.76

```