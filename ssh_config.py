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
SSH_CONFIG_PARSER = OneOrMore(HostBlock).ignore(pythonStyleComment)

class Host:
  attrs = [
    ('Host', str),
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
    self.__attrs = attrs

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
    with open(self.__path, 'r') as f:
      data = f.read()
    logger.debug("DATA: %s", data)
    parsed = SSH_CONFIG_PARSER.parseString(data)
    for name, config in parsed.asDict().items():
      attrs = dict()
      for attr in config:
        attrs.update(attr)
      self.__hosts.append(Host(name, attrs))
  
  @classmethod
  def load(cls, config_path):
    full_config_path = os.path.expanduser(config_path)
    logger.debug('Load: %s' % full_config_path)
    return cls(full_config_path)
  
  def __iter__(self):
    return self.__hosts.__iter__()

  def __next__(self):
    return self.__hosts.next()

def main(argv):
  parser = argparse.ArgumentParser()
  parser.add_argument('--config', default='~/.ssh/config')

  options, args = parser.parse_known_args(argv[1:])

  hosts = SSHConfig.load(options.config)
  for host in hosts:
      print('Name: %s, Config: %s' %(host.name, host.attributes))


if __name__ == '__main__':
  main(sys.argv)
