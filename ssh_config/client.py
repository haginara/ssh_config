from __future__ import print_function, absolute_import
import os
import logging
import subprocess  # call
from typing import List, Dict, Any
from pyparsing import (
    Literal,
    CaselessLiteral,
    CaselessKeyword,
    White,
    Word,
    alphanums,
    Empty,
    CharsNotIn,
    Forward,
    Group,
    SkipTo,
    Optional,
    OneOrMore,
    ZeroOrMore,
    pythonStyleComment,
    Dict,
    lineEnd,
    Suppress,
    indentedBlock,
    ParseException,
)

logger = logging.getLogger(__name__)


class EmptySSHConfig(Exception):
    def __init__(self, path):
        super().__init__("Empty SSH Config: %s" % path)


class WrongSSHConfig(Exception):
    def __init__(self, path):
        super().__init__("Wrong SSH Config: %s" % path)


class Host(object):
    attrs = [
        ("AddressFamily", str), # any, inet, inet6
        ("BatchMode", str),
        ("BindAddress", str),
        ("ChallengeResponseAuthentication", str), # yes, no
        ("CheckHostIP", str), # yes, no
        ("Cipher", str),
        ("Ciphers", str),
        ("ClearAllForwardings", str), # yes, no
        ("Compression", str), # yes, no
        ("CompressionLevel", int), # 1 to 9
        ("ConnectionAttempts", int), # default: 1
        ("ConnectTimeout", int),
        ("ControlMaster", str), # yes, no
        ("ControlPath", str), 
        ("DynamicForward", str), #[bind_address:]port, [bind_adderss/]port
        ("EnableSSHKeysign", str), # yes, no
        ("EscapeChar", str), #default: '~'
        ("ExitOnForwardFailure", str), #yes, no
        ("ForwardAgent", str), # yes, no
        ("ForwardX11", str), # yes, no
        ("ForwardX11Trusted", str), # yes, no
        ("GatewayPorts", str), # yes, no
        ("GlobalKnownHostsFile", str), # yes, no
        ("GSSAPIAuthentication", str), # yes, no
        ("HostName", str),
        ("User", str),
        ("Port", int),
        ("IdentityFile", str),
        ("LocalCommand", str),
        ("LocalForward", str),
        ("LogLevel", str),
        ("ProxyCommand", str),
        ("ProxyJump", str),
        ("Match", str),
        ("AddKeysToAgent", str),
        ("BindInterface", str),
        ("CanonialDomains", str),
        ("CnonicalizeFallbackLocal", str),
        ("IdentityAgent", str),
        ("PreferredAuthentications", str),
        ("ServerAliveInterval", int),
        ("UsePrivilegedPort", str), # yes, no
    ]

    def __init__(self, name, attrs):
        if isinstance(name, list):
            self.__name = name
        elif isinstance(name, str):
            self.__name = name.split() 
        else:
            raise TypeError
        self.__attrs = dict()
        attrs = {key.upper(): value for key, value in attrs.items()}
        for attr, attr_type in self.attrs:
            if attrs.get(attr.upper()):
                self.__attrs[attr] = attr_type(attrs.get(attr.upper()))

    def attributes(self, exclude=[], include=[]):
        if exclude and include:
            raise Exception("exclude and include cannot be together")
        if exclude:
            return {
                key: self.__attrs[key] for key in self.__attrs if key not in exclude
            }
        elif include:
            return {key: self.__attrs[key] for key in self.__attrs if key in include}
        return self.__attrs
    
    def __repr__(self) -> str:
        return f"Host<{self.name}>"

    def __str__(self):
        data = "Host %s\n" % self.name
        for key, value in self.__attrs.items():
            data += "    %s %s\n" % (key, value)
        return data

    def __getattr__(self, key):
        return self.__attrs.get(key)

    @property
    def name(self):
        return " ".join(self.__name)

    def update(self, attrs):
        if isinstance(attrs, dict):
            self.__attrs.update(attrs)
            return self
        raise AttributeError

    def get(self, key, default=None):
        return self.__attrs.get(key, default)

    def set(self, key: str, value):
        self.__attrs[key] = value

    def command(self, cmd: str="ssh"):
        if self.Port and self.Port != 22:
            port = "-p {port} ".format(port=self.Port)
        else:
            port = ""

        if self.User:
            user = "%s@" % self.User
        else:
            user = ""

        return "{cmd} {port}{username}{host}".format(
            cmd=cmd, port=port, username=user, host=self.HostName
        )
    
    def ansible(self):
        pass


class SSHConfig(object):
    def __init__(self, path: str):
        self.__path = path
        self.__hosts = []
        self.raw = None
    
    def __repr__(self) -> str:
        return f"SSHConfig<Path:{self.__path}>"

    @classmethod
    def load(cls, config_path: str):
        logger.debug("Load: %s" % config_path)
        ssh_config = cls(config_path)

        with open(config_path, "r") as f:
            ssh_config.raw = f.read()
        if len(ssh_config.raw) <= 0:
            raise EmptySSHConfig(config_path)
        # logger.debug("DATA: %s", data)
        parsed = ssh_config.parse()
        if parsed is None:
            raise WrongSSHConfig(config_path)
        for name, config in sorted(parsed.asDict().items()):
            attrs = dict()
            for attr in config:
                attrs.update(attr)
            ssh_config.append(Host(name, attrs))
        return ssh_config

    def parse(self, data: str=""):
        if data:
            self.raw = data

        SPACE = White().suppress()
        SEP = Suppress(SPACE) | Suppress("=")
        HOST = CaselessLiteral("Host").suppress()
        MATCH = CaselessLiteral("Match").suppress()
        KEY = Word(alphanums)
        VALUE = Word(alphanums + ' ~%*?!._-+/,"')
        paramValueDef = SkipTo("#" | lineEnd)
        indentStack = [1]

        HostDecl = (HOST | MATCH ) + SEP + VALUE
        paramDef = Dict(Group(KEY + SEP + paramValueDef))
        block = indentedBlock(paramDef, indentStack)
        HostBlock = Dict(Group(HostDecl + block))
        try:
            return OneOrMore(HostBlock).ignore(pythonStyleComment).parseString(self.raw)
        except ParseException as e:
            print(e)
            return None

    def __iter__(self):
        return self.__hosts.__iter__()

    def __next__(self):
        return self.__hosts.next()

    def __getitem__(self, idx: int):
        return self.__hosts[idx]

    def hosts(self):
        return self.__hosts

    def update(self, name: str, attrs: Dict):
        for idx, host in enumerate(self.__hosts):
            if name == host.name:
                host.update(attrs)
                self.__hosts[idx] = host

    def get(self, name: str, raise_exception=True):
        for host in self.__hosts:
            if host.name == name:
                return host
        if raise_exception:
            raise KeyError
        return None

    def append(self, host: Host):
        if not isinstance(host, Host):
            raise TypeError
        self.__hosts.append(host)

    def remove(self, name: str) -> bool:
        host = self.get(name, raise_exception=False)
        if host:
            self.__hosts.remove(host)
            return True
        return False

    def write(self, filename: str="") -> str:
        if filename:
            self.__path = filename
        with open(self.__path, "w") as f:
            for host in self.__hosts:
                f.write("Host %s\n" % host.name)
                for attr in host.attributes():
                    f.write("    %s %s\n" % (attr, host.get(attr)))
        return self.__path

    def asdict(self) -> Dict:
        return {host.name: host.attributes() for host in self.__hosts}
