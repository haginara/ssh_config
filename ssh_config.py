import os
import sys
import argparse
import logging
import pprint
from pyparsing import (
    Literal,
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
)

logger = logging.getLogger(__name__)


class Host:
  attrs = [
    ('HostName', str),
    ('Match',str),
    ('AddKeysToAgent',str),
    ('AddressFamily',str),
    ('BatchMode',str),
    ('BindAddress',str),
    ('BindInterface',str),
    ('CanonialDomains',str),
    ('CnonicalizeFallbackLocal',str),
    ('IdentityAgent',str),
    ('IdentityFile',str),
    ('LocalCommand',str),
    ('LocalForward',str),
    ('LogLevel',str),
    ('Port', int),
    ('PreferredAuthentications',str),
    ('ProxyCommand',str),
    ('User',str),
    ('ServerAliveInterval', int),
  ]
  def __init__(self, name, attrs):
    self.name = name
    self.__attrs = dict()

    for attr, attr_type in self.attrs:
      if attrs.get(attr):
        self.__attrs[attr] = attr_type(attrs.get(attr))


  @property
  def attributes(self):
    return self.__attrs
  
  def __getattr__(self, key):
    return self.__attrs.get(key)
  
  def get(self, key, default=None):
    return self.__attrs.get(key, default)
  
  def set(self, key, value):
    return self.__attrs.set(key, value)


class SSHConfig:
  def __init__(self, path):
    self.__path = path
    self.__hosts = []
    self.raw = None

  @classmethod
  def load(cls, config_path):
    logger.debug('Load: %s' % config_path)
    ssh_config = cls(config_path)
    
    with open(config_path, 'r') as f:
      ssh_config.raw = f.read()
    #logger.debug("DATA: %s", data)
    parsed = ssh_config.parse()
    for name, config in parsed.asDict().items():
      attrs = dict()
      for attr in config:
        attrs.update(attr)
      ssh_config.append(Host(name, attrs))
    return ssh_config
  
  def parse(self, data=""):
    if data:
      self.raw = data
    SPACE = White().suppress()
    HOST = Literal("Host").suppress()
    KEY = Word(alphanums + "~*._-/")
    VALUE = Word(alphanums + "~*._-/")
    paramValueDef = SkipTo("#" | lineEnd)
    indentStack = [1]

    HostDecl = HOST + SPACE + VALUE
    paramDef = Dict(Group(KEY + SPACE + paramValueDef))
    block = indentedBlock(paramDef, indentStack)
    HostBlock = Dict(Group(HostDecl + block))
    return OneOrMore(HostBlock).ignore(pythonStyleComment).parseString(self.raw)

  def __iter__(self):
    return self.__hosts.__iter__()

  def __next__(self):
    return self.__hosts.next()
  
  def __getitem__(self, idx):
    return self.__hosts[idx]
  
  def get(self, name):
    for host in self.__hosts:
      if host.name == name:
        return host
    raise KeyError
  
  def append(self, host):
    if not isinstance(host, Host):
      raise TypeError
    self.__hosts.append(host)
  
  def write(self, filename=""):
    if filename:
      self.__path = filename
    with open(self.__path, 'w') as f:
      for host in self.__hosts:
        f.write('Host %s\n' % host.name)
        for attr in host.attributes:
          f.write('    %s %s\n' % (attr, host.get(attr)))
    return self.__path


def main(argv):
  parser = argparse.ArgumentParser()
  parser.add_argument('--config', default='~/.ssh/config')

  options, args = parser.parse_known_args(argv[1:])
  options.config = os.path.expanduser(options.config)
  if not os.path.exists(options.config):
    answer = input("%s does not exists, Do you want to create new one[y/N]" % options.config)
    if answer == 'y':
      open(options.config, 'w').close()
      print("Created!")
    else:
      return
    config = SSHConfig(options.config)
  else:
    hosts = SSHConfig.load(options.config)
    for host in hosts:
      print('Name: %s, Config: %s' %(host.name, host.attributes))


if __name__ == '__main__':
  main(sys.argv)
