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
I don't remember all the servers I am managing. Also all servers require all different configurations to connect to it. I know ~.ssh/config can handle this kind of issue. I want it to handle this file easier.

Yes, I am not sure this is easier way to handle it. but I am trying.

Requirements
------------
   After 0.0.15, Python27 is not supported.

Python 3.6 or higher

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
       export      Export Hosts to csv/ansible format
       bastion     Bastion register/use
       ping        Send ping to selected host
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

### Export ssh-config to ansible inventory ini format.
```
ssh-config export ansible -g linux

[linux]
server1              ansible_host=203.0.113.76       
server_cmd_1         ansible_host=203.0.113.76       
server_cmd_2         ansible_host=203.0.113.76         ansible_user=user     
server_cmd_3         ansible_host=203.0.113.76         ansible_user=user     
```
