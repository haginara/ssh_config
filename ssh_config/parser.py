from __future__ import print_function, absolute_import
import logging
from pyparsing import (
    White,
    Word,
    alphas,
    Group,
    SkipTo,
    Dict,
    lineEnd,
    Suppress,
    ParseException,
)

logger = logging.getLogger("ssh_config")



class Line(object):
    """
    The first obtained avlue will be used.
    The configuration files contains sections seprated by Host specifictaions,
    and that section is only applied for hosts that match one of the patterns given in the speicifcation.
    """
    def __init__(self, idx, line, header_idx=None):
        self.idx = idx
        # comment, attribute, header
        self.line = line.strip()
        self.section = header_idx

        self._parse()

    def _parse(self):
        """
        The file contains keyword-argument pairs.
        one per line.
        Lines starting with '#' and empty lines are interpreted as comments
        Arguments may optionally by enclosed in double quote (") 
        in order to represent arguments containing spaces.
        Configuration options may be seprated by 
        whitespace or optional whitespace and 
        exactly one'='; 
        the latter format is usefule to avoid then eed to quote whitespace 
        when specifying confiugration options using the `ssh`, `scp`, `sftp -o` option.
        """
        pass


class Comment(Line):
    def __init__(self, idx, line, header_idx=None):
        super(Comment, self).__init__(idx, line, header_idx)

    def __str__(self):
        return f"Comment<{self.idx}>"

    def __repr__(self):
        return self.__str__()


class Option(Line):
    def __init__(self, idx, line, header_idx=None):
        super(Option, self).__init__(idx, line, header_idx)
        self.keyword = None
        self.argument = None

        self.parse()

    def __str__(self):
        return f"Option<{self.keyword}>:{self.argument}"

    def __repr__(self):
        return self.__str__()

    def parse(self):
        SPACE = White().suppress()
        # Configuration options may be seprated by
        # whitespace or optional whitespace and exactly one'='
        SEP = Suppress(SPACE) | Suppress("=")
        # note that keywords are case-insensitive and arguments are case-sensitive
        KEY = Word(alphas)
        # VALUE = Word(alphanums + ' ~%*?!._-+/,"')
        paramValueDef = SkipTo("#" | lineEnd)
        paramDef = Dict(Group(KEY + SEP + paramValueDef))
        try:
            self.keyword, self.argument = paramDef.parseString(self.line)[0]
            logger.debug(paramDef.parseString(self.line))
        except ParseException as e:
            logger.error("Failed to parse string: %s" % (self.line))
            raise e


class Header(Option):
    def __str__(self):
        return f"Header<{self.keyword}>:{self.argument}"

    def __repr__(self):
        return self.__str__()


class Section:
    """ SSHConfig Section
    """
    def __init__(self, header):
        self.header = header
        self.options = []

    def add(self, option):
        assert type(option) == Option
        self.options.append(option)


class SSHConfig:
    def __init__(self, path: str):
        self.config_path = path
        sections = self.parse(self.read(self.config_path))

        self.defaults = sections[0].options
        self.sections = sections[1:]

    def __str__(self):
        return f"SSHConfig<{self.config_path}>"

    def __repr__(self):
        return self.__str__()

    def read(self, path):
        with open(path) as f:
            lines = [line.strip() for line in f.readlines()]

        for line in lines:
            yield line

    def parse(self, reader):
        section = Section(None)
        sections = []
        for idx, line in enumerate(reader):
            if line.startswith("#") or len(line.strip()) == 0:
                # section.add(Comment(idx, line))
                continue
            # Header Option, it starts the new section
            elif line[:4].upper() == 'HOST' and line[4] in ['=', ' ']:
                sections.append(section)
                section = Section(Header(idx, line))
            elif line[:5].upper() == 'MATCH' and line[5] in ['=', ' ']:
                sections.append(section)
                section = Section(Header(idx, line))
            # Options for Section
            else:
                section.add(Option(idx, line))
        sections.append(section)
        return sections


# ==============================================
# TEST
# ==============================================

def test_parse():
    config = SSHConfig('tests/sample')

    # Default option
    assert config.defaults[0].keyword == "CompressionLevel"
    assert config.defaults[0].argument == "1"

    # Sections
    assert type(config.sections[1].header) == Header
    assert type(config.sections[1].options[0]) == Option

    section = config.sections[1]
    assert section.header.argument == '*'
    assert section.options[0].keyword == 'ServerAliveInterval'

    last = config.sections[-1]
    assert last.header.argument == "unidentifieed_host"
    assert last.options[0].argument == '127.0.0.1'
    assert last.options[2].keyword == 'User'


if __name__ == '__main__':
    from pprint import pprint
    reader = read('tests/sample')
    lines = [line for line in parse(reader)]
    sections = {}
    for token in lines:
        if token.section in sections:
            sections[token.section].append(token)
        else:
            sections[token.section] = [token]
    for section in sections:
        pprint([section, sections[section]])
