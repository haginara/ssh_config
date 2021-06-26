from __future__ import print_function, absolute_import

import os
import logging
from pyparsing import (
    CaselessLiteral,
    White,
    Word,
    alphanums,
    Group,
    SkipTo,
    OneOrMore,
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


class HostExistsError(Exception):
    def __init__(self, name):
        super().__init__(f"Host already exists, {name}")


class Host(object):
    """
    Host object contains information of Host
    """
    attrs = [
        ("AddressFamily", str),  # any, inet, inet6
        ("BatchMode", str),
        ("BindAddress", str),
        ("ChallengeResponseAuthentication", str),  # yes, no
        ("CheckHostIP", str),  # yes, no
        ("Cipher", str),
        ("Ciphers", str),
        ("ClearAllForwardings", str),  # yes, no
        ("Compression", str),  # yes, no
        ("CompressionLevel", int),  # 1 to 9
        ("ConnectionAttempts", int),  # default: 1
        ("ConnectTimeout", int),
        ("ControlMaster", str),  # yes, no
        ("ControlPath", str),
        ("DynamicForward", str),  # [bind_address:]port, [bind_adderss/]port
        ("EnableSSHKeysign", str),  # yes, no
        ("EscapeChar", str),  # default: '~'
        ("ExitOnForwardFailure", str),  # yes, no
        ("ForwardAgent", str),  # yes, no
        ("ForwardX11", str),  # yes, no
        ("ForwardX11Trusted", str),  # yes, no
        ("GatewayPorts", str),  # yes, no
        ("GlobalKnownHostsFile", str),  # yes, no
        ("GSSAPIAuthentication", str),  # yes, no
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
        ("ServerAliveCountMax", int),
        ("UsePrivilegedPort", str),  # yes, no
        ("TCPKeepAlive", str),  # yes, no
    ]

    def __init__(self, name, attrs):
        self.set_name(name)
        self.__attrs = dict()
        attrs = {key.upper(): value for key, value in attrs.items()}
        for attr, attr_type in self.attrs:
            if attrs.get(attr.upper()):
                self.__attrs[attr] = attr_type(attrs.get(attr.upper()))

    def set_name(self, name):
        """
        Set Host name

        args:
            name (list or str)
        """
        if isinstance(name, list):
            self.__name = name
        elif isinstance(name, str):
            self.__name = name.split()
        else:
            raise TypeError

    def __repr__(self):
        return f"Host<{self.name}>"

    def __str__(self):
        data = "Host %s\n" % self.name
        for key, value in self.__attrs.items():
            data += "    %s %s\n" % (key, value)
        return data

    def __getattr__(self, key):
        return self.__attrs.get(key)

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

    @property
    def name(self):
        return " ".join(self.__name)

    def update(self, attrs: Dict):
        if isinstance(attrs, dict):
            self.__attrs.update(attrs)
            return self
        raise AttributeError

    def get(self, key, default=None):
        """Get value by key name

        args:
            key (str)
            default (any)
        returns:
            value or None
        """
        return self.__attrs.get(key, default)

    def set(self, key: str, value):
        self.__attrs[key] = value

    def command(self, cmd="ssh"):
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
    """ ssh_config file.
    """
    __slots__ = ['hosts', 'raw', 'config_path']

    def __init__(self, path=None):
        """
        Initialize an instance of a ssh_config file
        params:
             path(str or None): the path of ssh_config file to manage
        
        returns:
            None
        """
        
        self.hosts = []
        self.raw = None
        if path is None:
            self.config_path = os.path.expanduser("~/.ssh/config")
        else:
            self.config_path = path
        
        self.load_hosts()
    

    def __repr__(self) -> str:
        return f"SSHConfig<Path:{self.config_path}>"

    def __iter__(self):
        return self.hosts.__iter__()

    def __next__(self):
        return self.hosts.next()

    def __getitem__(self, name):
        return self.get(name)

    @classmethod
    def create(cls, config_path: str):
        """ 
        Load ssh-config file with path

        params:
            config_path (str): path of ssh_config file

        returns:
            SSHConfig
        """
        logger.debug("Create: %s" % config_path)
        if os.path.exists(config_path):
            raise FileExistsError(config_path)
        open(config_path, 'w').write("")
        ssh_config = cls(config_path)
        return ssh_config

    def load_hosts(self):
        """
        Load the ssh_config file into `hosts` with config_path
        """
        try:
            with open(self.config_path, 'r') as f:
                self.raw = f.read()
                if len(self.raw) < 1:
                    "If file is empty, it returns None"
                    return None
                parsed = self.parse()
                if parsed is None:
                    raise WrongSSHConfig(self.config_path)
                for name, config in sorted(parsed.asDict().items()):
                    attrs = {}
                    for attr in config:
                        attrs.update(attr)
                    self.hosts.append(Host(name, attrs))
        except IOError as e:
            raise e

    def parse(self, data=""):
        """
        Parse ssh-config data from raw data

        args:
            data (str)

        returns:
            Parsed config or None (dict)
        """

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

        HostDecl = (HOST | MATCH) + SEP + VALUE
        paramDef = Dict(Group(KEY + SEP + paramValueDef))
        block = indentedBlock(paramDef, indentStack)
        HostBlock = Dict(Group(HostDecl + block))

        try:
            parsed = OneOrMore(HostBlock).ignore(pythonStyleComment).parseString(self.raw)
        except ParseException as e:
            return None

        return parsed

    def update(self, name: str, attrs: Dict):
        """
        Update the host with name and attributes

        params:
            name (str): Name of Host
            attrs (dict): Attributes
        
        returns:
            None
        """
        idx, host = self.get_host_with_index(name)
        host.update(attrs)
        self.hosts[idx] = host
        
    def rename(self, name: str, new_name: str):
        """
        Rename the host name(pattern)

        args:
            name: old name
            new_name: new name
        
        returns:
            None
        """
        idx, host = self.get_host_with_index(name)
        host.setname(new_name)
        self.hosts[idx] = host

    def exists(self, name: str):
        """
        Check exist the host with name

        args:
            name (str): host name
        
        returns:
            bool
        """
        try:
            self.get_host_with_index(name)
        except NameError:
            return False
        return True

    def get(self, name: str):
        """
        get Host with name

        args:
            name (str): host name
        
        returns:
            Host
        """
        idx, host = self.get_host_with_index(name)
        return host
        

    def add(self, host: Host):
        """
        Add host to ssh config object

        args:
            host (Host): Host object to add
        """
        if not isinstance(host, Host):
            raise TypeError
        try:
            self.get(host.name)
        except NameError:
            self.hosts.append(host)
            return
        raise HostExistsError(host.name)

    def remove(self, name: str):
        """
        Remove the host with name

        args:
            name (str): host name
        """
        idx, host = self.get_host_with_index(name)
        self.hosts.remove(host)
        

    def write(self, filename=None):
        """
        Write the current ssh_config to self.config_path or given filename

        It chagnes the self.config_path, if the filename is given.
        args:
            filename (str): target filename to be written.
        """
        if filename:
            self.config_path = filename

        with open(self.config_path, "w") as f:
            for host in self.hosts:
                f.write(f"Host {host.name}\n")
                for attr in host.attributes():
                    f.write(f"{' '*4}{attr} {host.get(attr)}\n")

    def asdict(self):
        """
        Return dict from list of hosts

        returns:
            hosts (List[dict])
        """
        hosts = []
        for host in self.hosts:
            host_dict = {'Host': host.name}
            host_dict.update(host.attributes())
            hosts.append(host_dict)
        return hosts
    
    def get_host_with_index(self, name: str):
        """
        Get host object with index
        
        args:
            name (str): host name

        returns:
            idx, Host
        """
        for idx, host in enumerate(self.hosts):
            if name == host.name:
                return idx, host
        raise NameError(f"No name found in config, {name}")