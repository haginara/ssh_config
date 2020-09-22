SSH Config
==========
[![PyPI version](https://badge.fury.io/py/ssh-config.svg)](https://badge.fury.io/py/ssh-config)
[![Build Status](https://travis-ci.org/haginara/ssh_config.svg?branch=master)](https://travis-ci.org/haginara/ssh_config)

SSH client config file manager


What is ssh_config?
-------------------
https://linux.die.net/man/5/ssh_config

Why
---
I don't remember all the servers I am managing. Also all servers requires all different configuration to connec to it. I know ~.ssh/config can handle this kind of issue. I want it to handle this file easier.

Yes, I am not sure this is eaiser way to handle it. but I am trying.

Requirements
------------
After 0.0.15, Python27 is not supported.
Python 2.7, 3.6, 3.7

Installation
------------
```
$ pip install ssh-config
```

Usage
-----
```
ssh-config <version>

    Usage:
        ssh-config [options] [COMMAND] [ARGS...]

    Options:
        -h --help           Show this screen.
        -v --version        Show version.
        -f --config FILE    Specify an ssh client file [default: ~/.ssh/config]

    Commands:
        ls          Show list of Hosts in client file
        add         Add new Host configuration
        rm          Remove exist Host configuration
        init        Create ~/.ssh/config file
        import      Import Hosts from csv file to SSH Client config
        export      Export Hosts to csv format
        bastion     Bastion register/use
        version     Show version information
```

Use-cases
---------

#### List hosts
```
$ ssh-config ls 
# It shows name and HostName attribute
server1: 203.0.113.76
*: None
server_cmd_1: 203.0.113.76
server_cmd_2: 203.0.113.76
server_cmd_3: 203.0.113.76
```

##### Add host
```
$ ssh-config add "server_cmd_4" HostName=203.0.113.77 IdentityFile="~/.ssh/cmd_id_rsa"
```

##### Update host
```
$ ssh-config add --update -p "server_cmd_3" IdentityFile="~/.ssh/cmd_id_rsa"
```

##### Remove host
```
$ ssh-config rm "server_3" 
```

### Using pattern to get list or update exist hosts

##### List hosts with pattern
```
$ ssh-config ls "server_*"
# It shows name and HostName attribute
server_cmd_1: 203.0.113.76
server_cmd_2: 203.0.113.76
server_cmd_3: 203.0.113.76
```

##### Update hosts with pattern
```
$ ssh-config add --update -p "server_*" IdentityFile="~/.ssh/cmd_id_rsa"
```


#### add ssh key to multiple servers
```
ssh-config ls --only-name | xargs -I{} ssh-copy-id -i ~/.ssh/id_rsa {}
```
