import os
import csv
import fnmatch


from ..client import Host

from .base import BaseCommand
from .base import ArgumentRequired
from .utils import table_print, simple_print, field_print, grep, input_is_yes


class Get(BaseCommand):
    """Get hosts.

    usage: get [options] [PATTERN]

    Options:
        -h --help           Show this screen
    """

    def execute(self):
        pattern = self.options.get("PATTERN", None)
        if pattern is None:
            raise ArgumentRequired
        # Print plain
        target = grep(pattern, table_print())
        for host in self.config:
            target.send(host)


class Ls(BaseCommand):
    """List hosts.

    usage: ls [options] [PATTERN]

    Options:
        --only-name             Print name only
        --fields [FIELD...]     Print selected fields, fielda are spliited by ','
        -v --verbose            Verbose output
        -h --help               Show this screen
    """

    def execute(self):
        only_name = self.options.get("--only-name")
        fields = self.options.get("--fields")
        pattern = self.options.get("PATTERN", None)
        verbose = self.options.get("--verbose")

        if only_name:
            printer = simple_print()
        elif fields:
            printer = field_print(fields)
        else:
            printer = table_print(verbose)

        target = grep(pattern, printer)
        for host in self.config:
            target.send(host)


class Add(BaseCommand):
    """Add host.

    Usage: add [options] (HOSTNAME) <attribute=value>...

    Options:
        --update            If host exists, update it.
        -b --bastion        Add attributes for Bastion host
        -p --use-pattern    Use pattern to find hosts
        -y --yes            Force answer yes
        -v --verbose        Verbose Output
        -h --help           Shwo this screen

    Attributes:
        {% for attr, attr_type in attrs %}
        {{ attr }}
        {% endfor %}
    """

    def execute(self):
        verbose = self.options.get("--verbose")
        hostname = self.options.get("HOSTNAME")
        attrs = self.options.get("<attribute=value>", [])
        is_bastion = self.options.get("--bastion")
        try:
            attrs = {
                attr.split("=")[0]: attr.split("=")[1]
                for attr in self.options.get("<attribute=value>", [])
            }
        except Exception as e:
            raise Exception(f"<attribute=value> like options aren't provided, {e}, {self.options.get('<attribute=value>')}")
        if is_bastion:
            attrs.update({"ProxyCommand": "none", "ForwardAgent": "yes"})
        use_pattern = self.options.get("--use-pattern")
        if use_pattern:
            """ use-pattern is only accept update, not add """
            hosts = [
                host for host in self.config if fnmatch.fnmatch(host.name, hostname)
            ]
            if hosts:
                for host in hosts:
                    self.config.update(host.name, attrs)
            else:
                print("No hosts found")
                return
        else:
            host = self.config.get(hostname, raise_exception=False)
            if self.options.get("--update"):
                if not host:
                    print("No host to be updated, %s" % hostname)
                if verbose:
                    print("Update attributes: %s" % attrs)
                self.config.update(hostname, attrs)
            else:
                if host:
                    print("%s host already exist" % hostname)
                    return
                host = Host(hostname, attrs)
                self.config.append(host)

        if self.options.get("--verbose"):
            print("%s" % host)
        if self.options.get("--yes") or input_is_yes(
            "Do you want to save it", classault="n"
        ):
            self.config.write()


class Rm(BaseCommand):
    """Remove Host.
    Usage: rm [options] (HOSTNAME)

    Options:
        -v --verbose    Verbose output
        -y --yes        Force answer yes
        -h --help       Show this screen
    """

    def execute(self):
        verbose = self.options.get("--verbose")
        hostname = self.options.get("HOSTNAME")
        host = self.config.get(hostname, raise_exception=False)
        if host is None:
            print("No hostname")
            return
        if verbose:
            print("%s" % host)
        self.config.remove(hostname)
        if self.options.get("--yes") or input_is_yes(
            "Do you want to remove %s" % hostname, classault="n"
        ):
            self.config.write()


class Import(BaseCommand):
    """Import hosts.
    Usage: import [options] (FILE)

    Options:
        -v --verbose    Verbose output
        -q --quiet      Quiet output
        -y --yes        Force answer yes
        -h --help       Show this screen
    """

    def execute(self):
        queit = self.options.get("--quiet")
        csv_file = self.options.get("FILE")
        if not csv_file or not os.path.exists(csv_file):
            print("No FILE")
            return
        with open(csv_file) as csvfile:
            reader = csv.DictReader(csvfile)
            if "Name" not in reader.fieldnames:
                print("No Name field")
                return
            for field in reader.fieldnames[1:]:
                if field not in [attr[0] for attr in Host.attrs]:
                    print("Unallowed attribute exist: %s" % field)
                    return
            for row in reader:
                hostname = row.pop("Name")
                host = Host(hostname, row)
                self.config.append(host)
                if not queit:
                    print("Import: %s, %s" % (host.name, host.HostName))

        if self.options.get("--yes") or input_is_yes(
            "Do you want to save it", classault="n"
        ):
            self.config.write()


class Export(BaseCommand):
    """Export hosts.
    Usage: export [options] ([FORMAT] <file> | <file>)
    
    Options:
        -x                  Export only essential fields
        -g --group GROUP    Name of group
        -c columns          Column names, A comma separted list of field names. 
        -h --help           Show this screen
        -v --verbose        Verbose output
        -q --quiet          Quiet output
        -y --yes            Forcily yes
    
    Format:
        csv [classault]
    """

    def execute(self):
        quiet = self.options.get("--quiet")
        verbose = self.options.get("--verbose")
        essential = self.options.get("-x")
        group = self.options.get("--group")
        fields = self.options.get("-c").split(",") if self.options.get("-c") else []
        outfile = self.options.get("<file>")
        outformat = self.options.get("FORMAT") or "csv"
        if os.path.exists(outfile):
            print("%s exists." % outfile)
            if not self.options.get("--yes") and not input_is_yes(
                "Do you want to overwrite it", classault="n"
            ):
                return

        with open(outfile, "w") as f:
            if outformat == "csv":
                if essential:
                    header = ["HostName", "User", "Port", "IdentityFile"]
                elif fields:
                    header = fields
                else:
                    header = [attr for attr, attr_type in Host.attrs]

                writer = csv.DictWriter(
                    f, fieldnames=["Name"] + header, lineterminator="\n"
                )
                writer.writeheader()
                for host in self.config:
                    row = {"Name": host.name}
                    row.update(host.attributes(include=header))
                    writer.writerow(row)
            elif outformat == "ansible":
                """
                in INI
                jumper ansible_port=5555 ansible_host=192.0.2.50
                in YAML
                hosts:
                    jumper:
                        ansible_port: 5555
                        ansible_host: 192.0.2.50
                """
                if group:
                    f.write("[%s]\n" % group)
                for host in self.config:
                    if host.name == "*":
                        continue
                    line = "{:<20}ansible_host={:<20}".format(host.name, host.HostName)
                    if host.User:
                        line += "ansible_user={:<10}".format(host.User)
                    if host.IdentityFile:
                        line += "ansible_ssh_private_key_file={:<20}".format(
                            os.path.expanduser(host.IdentityFile)
                        )
                    if verbose:
                        print(line)
                    f.write("%s\n" % line)


class Bastion(BaseCommand):
    """Manage Bastion hosts
    Usage: bastion [options] <bastion> <server>...
    
    Options:
        -h --help           Show this screen
        -v --verbose        Verbose output
        -y --yes            Forcily yes
    """

    def execute(self):
        verbose = self.options.get("--verbose")
        bastion = self.options.get("<bastion>")
        servers = self.options.get("<server>", [])

        bastion_host = self.config.get(bastion)
        forward_agent = bastion_host.get("ForwardAgent", None)
        if forward_agent is None or forward_agent != "yes":
            print("%s is not bastion server" % bastion)
            return

        for server in servers:
            host = self.config.get(server, raise_exception=False)
            if host is None:
                print("%s does not exist" % server)
                return
            if host.get("ProxyCommand", None):
                if not self.options.get("--yes") and not input_is_yes(
                    "%s has ProxyComamnd, %s" % (host, host.ProxyCommand), classault="n"
                ):
                    return
            host.set("ProxyCommand", "ProxyCommand ssh -q -A bastion -W %h:%p")
