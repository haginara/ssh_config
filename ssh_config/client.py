"""SSH Config client
"""
from typing import List, Dict, Tuple
import os
import re
import logging

HOST_START = re.compile(r'^(host|match)[ =](?P<name>.*)', re.IGNORECASE)


logger = logging.getLogger("ssh_config.client")


class EmptySSHConfig(Exception):
    """Exception"""
    def __init__(self, path):
        super().__init__("Empty SSH Config: %s" % path)


class WrongSSHConfig(Exception):
    """Exception"""
    def __init__(self, path):
        super().__init__("Wrong SSH Config: %s" % path)


class HostExistsError(Exception):
    """Exception"""
    def __init__(self, name):
        super().__init__(f"Host already exists, {name}")


def is_skip(line):
    """Check the lins can be skipped"""
    if line == '':
        return True
    if line[0] == '#':
        return True
    return False


def remove_comment(line):
    """Remove the comment on the line"""
    if line.find('#') != -1:
        line = line[:line.find('#')]
    return line


def get_attribute(line):
    """Get attribute from the line"""
    delim = ' '
    if '=' in line:
        delim = '='
    try:
        key, value = line.split(delim, 1)
    except ValueError as error:
        raise Exception(f"Failed to split, {line}, delim: '{delim}'") from error
    return key.strip(), value.strip()


def parse_config(data: str) -> Tuple[List, Dict]:
    """Parse the ssh config
    Args:
        data (str): SSH Config string
    Returns:
        (list, dict): List of hosts and global Attirbutes
    Raises:
        No File Exists
    """
    if not isinstance(data, str):
        raise ValueError(f"Required str type, not {type(data)}")
    hosts = []
    global_options = {}
    host = None
    for line in data.splitlines():
        # START: Preprocessing
        line = line.strip()
        # Skip the whitespace
        if is_skip(line):
            continue
        line = remove_comment(line)
        # END: Preprocessing
        # Parsing Host/Match
        match = HOST_START.match(line)
        if match:
            if host:
                hosts.append(host)
            name = match.group('name')
            host = {'host': name, 'attrs': {}}
            continue
        # Parsing Attributes
        key, value = get_attribute(line)
        if host:
            host['attrs'][key] = value
        else:
            global_options[key] = value
    if host:
        hosts.append(host)
    return hosts, global_options


def read_config(path: str) -> Tuple[List, Dict]:
    """Read the ssh config from path
    Args:
        path (str): ssh config path
    Returns:
        (list, dict): List of hosts and global Attirbutes
    Raises:
        No File Exists
    """
    if not os.path.exists(path):
        raise Exception(f"No file exist, {path}")
    with open(path) as f:
        hosts, global_options = parse_config(f.read())
    return hosts, global_options


def test_read_config():
    """Test for read_config."""
    hosts, global_attrs = read_config('../tests/sample')
    for host in hosts:
        print(host)
    assert len(hosts) == 6
    assert global_attrs['CanonicalizeHostname'] == 'no'


class Host:
    """Host object contains information of Host"""
    attrs = [
        ("HostName", str),
        ("User", str),
        ("Port", int),
        ("IdentityFile", str),
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
        ("LocalCommand", str),
        ("LocalForward", str),
        ("LogLevel", str),
        ("ProxyCommand", str),
        ("ProxyJump", str),
        ("Match", str),
        ("AddKeysToAgent", str),
        ("BindInterface", str),
        ("CanonicalizeHostname", str),  # yes, no
        ("CanonicalizeMaxDots", int),
        ("CanonicalDomains", str),
        ("CanonicalizePermittedCNAMEs", str),
        ("CanonicalizeFallbackLocal", str),
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
        """Set Host name
        Args:
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
        data = f"Host {self.name}\n"
        for key, value in self.__attrs.items():
            data += f"    {key} {value}\n"
        return data

    def __getattr__(self, key):
        return self.__attrs.get(key)

    def attributes(self, exclude=None, include=None):
        """Get attributes
        Args:
            exclude (List or None): Attributes to exclude
            include (List or None): Atrributes to include
        """
        if exclude and include:
            raise Exception("exclude and include cannot be together")
        if exclude:
            return {
                key: self.__attrs[key] for key in self.__attrs if key not in exclude
            }
        if include:
            return {key: self.__attrs[key] for key in self.__attrs if key in include}
        return self.__attrs

    @property
    def name(self):
        """Return name"""
        return " ".join(self.__name)

    def update(self, attrs: Dict):
        """Update the attributes"""
        if isinstance(attrs, dict):
            self.__attrs.update(attrs)
            return self
        raise AttributeError

    def get(self, key, default=None):
        """Get value by key name
        Args:
            key (str)
            default (any)
        Returns:
            value or None
        """
        return self.__attrs.get(key, default)

    def set(self, key: str, value):
        """Set attribute"""
        self.__attrs[key] = value

    def command(self, cmd="ssh"):
        """Return the ssh command based on option"""
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
        """Return the ansible."""
        pass


class SSHConfig:
    """ssh_config file."""
    __slots__ = ["hosts", "raw", "config_path", "global_options"]

    def __init__(self, path=None):
        """Initialize an instance of a ssh_config file
        Args:
             path(str or None): the path of ssh_config file to manage
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
        """Load ssh-config file with path
        Args:
            config_path (str): path of ssh_config file
        Returns:
            SSHConfig
        """
        logger.debug("Create: %s", config_path)
        if os.path.exists(config_path):
            raise FileExistsError(config_path)
        open(config_path, "w").write("")
        ssh_config = cls(config_path)
        return ssh_config

    def load_hosts(self):
        """Load the ssh_config file into `hosts` with config_path"""
        hosts, global_options = read_config(self.config_path)
        for host in hosts:
            self.hosts.append(Host(host['host'], host['attrs']))
        self.global_options = global_options

    def update(self, name: str, attrs: Dict):
        """Update the host with name and attributes
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
        """Rename the host name(pattern)
        Args:
            name: old name
            new_name: new name
        Returns:
            None
        """
        idx, host = self.get_host_with_index(name)
        host.setname(new_name)
        self.hosts[idx] = host

    def exists(self, name: str):
        """Check exist the host with name
        Args:
            name (str): host name
        Returns:
            bool
        """
        try:
            self.get_host_with_index(name)
        except NameError:
            return False
        return True

    def get(self, name: str):
        """Get Host with name
        Args:
            name (str): host name
        Returns:
            Host
        """
        _, host = self.get_host_with_index(name)
        return host

    def add(self, host: Host):
        """Add host to ssh config object
        Args:
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
        """Remove the host with name
        Args:
            name (str): host name
        """
        _, host = self.get_host_with_index(name)
        self.hosts.remove(host)

    def write(self, filename=None):
        """Write the current ssh_config to self.config_path or given filename
        It chagnes the self.config_path, if the filename is given.
        Args:
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
        """Return dict from list of hosts
        Returns:
            hosts (List[dict])
        """
        hosts = []
        for host in self.hosts:
            host_dict = {"Host": host.name}
            host_dict.update(host.attributes())
            hosts.append(host_dict)
        return hosts

    def get_host_with_index(self, name: str):
        """Get host object with index
        Args:
            name (str): host name
        Returns:
            idx, Host
        """
        for idx, host in enumerate(self.hosts):
            if name == host.name:
                return idx, host
        raise NameError(f"No name found in config, {name}")
