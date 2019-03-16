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

SPACE = White().suppress()
HOST = Literal("Host").suppress()
KEY = Word(alphanums + "*._/")
VALUE = Word(alphanums + "*._/")
paramValueDef = SkipTo("#" | lineEnd)
indentStack = [1]


paramDef = Forward()
HostDecl = (HOST + SPACE + VALUE)
block = indentedBlock(paramDef, indentStack)
paramDef << Dict(Group(KEY + SPACE + VALUE))
HostBlock = Dict(Group(HostDecl + block))
parser = OneOrMore(HostBlock).ignore(pythonStyleComment)


data = open(os.path.expanduser('~/.ssh/config'), 'r').read()
sample = """
Host server1
  ServerAliveInterval 200
  HostName 203.0.113.76
Host * 
  ExitOnForwardFailure yes
  Protocol 2
  ServerAliveInterval 400
"""
parsed = parser.parseString(data).asDict()
for host in parsed:
    print("Host: %s" % host)
    for option in parsed[host]:
        print("\t%s" % option)
