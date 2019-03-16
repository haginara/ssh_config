import os
import argparse
import pprint
from pyparsing import (
    Literal,
    White,
    Word,
    alphanums,
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

class SSHConfig:
  SPACE = White().suppress()
  HOST = Literal("Host").suppress()
  KEY = Word(alphanums + "~*._-/")
  VALUE = Word(alphanums + "~*._-/")
  paramValueDef = SkipTo("#" | lineEnd)
  indentStack = [1]


  paramDef = Forward()
  HostDecl = (HOST + SPACE + VALUE)
  block = indentedBlock(paramDef, indentStack)
  paramDef << Dict(Group(KEY + SPACE + VALUE))
  HostBlock = Dict(Group(HostDecl + block))
  parser = OneOrMore(HostBlock).ignore(pythonStyleComment)

  def __init__(self, host, config):
    self.host = host
    self.config = config
  
  @classmethod
  def load(cls, config_path):
    full_config_path = os.path.expanduser(config_path)
    with open(full_config_path, 'r') as f:
      parsed = SSHConfig.parser.parseString(f.read()).asDict()
    return [ cls(host, parsed[host]) for host in parsed ]


