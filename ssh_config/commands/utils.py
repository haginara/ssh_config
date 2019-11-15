import fnmatch
import os
import json
from typing import Dict, List

from texttable import Texttable



def input_is_yes(msg, default="n"):
    if default not in ["y", "n"]:
        raise Exception("Only accept 'y' or 'n'")
    if default is "n":
        msg += " [yN]? "
    else:
        msg += " [Yn]? "
    answer = input(msg)
    if len(answer) == 1 and answer[0].upper() == "Y":
        return True
    return False


def coroutine(func):
    def start(*args, **kwargs):
        cr = func(*args, **kwargs)
        next(cr)
        return cr

    return start


@coroutine
def grep(pattern, target):
    while True:
        host = yield
        name = host.name
        hostname = str(host.HostName)
        if (
            pattern is None
            or fnmatch.fnmatch(host.name, pattern)
            or pattern in name
            or pattern in hostname
        ):
            target.send(host)


@coroutine
def simple_print():
    while True:
        host = yield
        print(host.name)


@coroutine
def field_print(fields):
    while True:
        host = yield
        row = ",".join([getattr(host, field) for field in fields.split(",") if getattr(host, field)])
        print(row)


@coroutine
def table_print(verbose=False):
    ## Print Table
    table = Texttable(max_width=100)
    table.set_deco(Texttable.HEADER)
    header = ["Host", "HostName", "User", "Port", "IdentityFile"]
    if verbose:
        table.header(header + ["Others"])
    else:
        table.header(header)

    try:
        while True:
            host = yield
            if verbose:
                others = "\n".join(
                    [
                        "%s %s" % (key, value)
                        for key, value in host.attributes(exclude=header).items()
                    ]
                )

                table.add_row(
                    [
                        host.name,
                        host.HostName,
                        host.User,
                        host.Port,
                        host.IdentityFile,
                        others,
                    ]
                )
            else:
                table.add_row(
                    [host.name, host.HostName, host.User, host.Port, host.IdentityFile]
                )
    except GeneratorExit:
        print(table.draw() + "\n")
