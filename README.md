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
pip3 install ssh-config
```

Usage
-----
```
Usage: ssh-config [OPTIONS] COMMAND [ARGS]...

Options:
  -f, --path TEXT       [default: /Users/jonghak.choi/.ssh/config]
  --debug / --no-debug
  --version             Show the version and exit.
  --help                Show this message and exit.

Commands:
  add         Add SSH Config into config file
  attributes  Print possible attributes for Host
  gen         Generate the ssh config
  get         Get ssh config with name
  ls          Enumerate the configs
  remove
  rename
  ssh         Interative shell for Host
  update      Update the ssh Host config Attribute key=value format
```

Use-cases
---------

#### List hosts
```
$ ssh-config ls
server1
server_cmd_1
server_cmd_2
server_cmd_3

$ ssh-config ls -l
server1			10.0.2.10
server_cmd_1	10.0.1.11
server_cmd_2	10.0.1.12
server_cmd_3	10.0.1.13
```

##### Add host
```
$ ssh-config add "server_cmd_4" HostName=203.0.113.77 IdentityFile="~/.ssh/cmd_id_rsa"
```

##### Update host
```
$ ssh-config update "server_cmd_3" IdentityFile="~/.ssh/cmd_id_rsa"
```

##### Remove host
```
$ ssh-config remove "server_3"
```

### Using pattern to get list or update exist hosts

#### add ssh key to multiple servers
```
ssh-config ls | xargs -I{} ssh-copy-id -i ~/.ssh/id_rsa {}
```

### Export ssh-config to ansible inventory ini format.
https://docs.ansible.com/ansible/latest/dev_guide/developing_inventory.html?extIdCarryOver=true&sc_cid=701f2000001OH7EAAW#inventory-script-conventions
```
ssh-config inventory --list|--host <hostname>
```
