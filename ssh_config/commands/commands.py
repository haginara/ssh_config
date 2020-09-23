import os
import stat
import csv
import platform
import fnmatch

from subprocess import run
from jinja2 import Template

from ..client import Host

from .base import BaseCommand
from .base import ArgumentRequired
from .utils import table_print, simple_print, field_print, ssh_format_print, grep, input_is_yes


class Gen(BaseCommand):
    """Generate empty ssh-config file

    usage: gen

    Options:
        -h --help           Show this screen
    """

    def execute(self):
        open(self.config, "w").close()
        os.chmod(self.config, stat.S_IREAD | stat.S_IWRITE)
        print("Created!")


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
        -v, --verbose           Verbose output
        -s, --ssh-format        Print ssh-login format
        -h, --help              Show this screen
    """

    def execute(self):
        only_name = self.options.get("--only-name")
        fields = self.options.get("--fields")
        pattern = self.options.get("PATTERN", None)
        verbose = self.options.get("--verbose")
        ssh_format = self.options.get("--ssh-format")

        if only_name:
            printer = simple_print()
        elif fields:
            printer = field_print(fields)
        if ssh_format:
            printer = ssh_format_print()
        else:
            printer = table_print(verbose)

        target = grep(pattern, printer)
        for host in self.config:
            target.send(host)


class Add(BaseCommand):
    """Add host.

    Usage: add [options] <HOSTNAME> <attribute=value>...

    Arguments:
        HOSTNAME Host name

    Options:
        -b,--bastion        Add attributes for Bastion host
        -y,--yes            Force answer yes
        -h,--help           Shwo this screen

    Attributes:
        {% for attr, attr_type in attrs %}
        {{ attr }}
        {% endfor %}
    """
    def pre_command(self):
        template = Template(self.__doc__, trim_blocks=True, lstrip_blocks=True)
        self.__doc__ = template.render(attrs=Host.attrs)

    def execute(self):
        hostname = self.options.get("<HOSTNAME>")
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

        host = self.config.get(hostname, raise_exception=False)
        if host:
            print("%s host already exist" % hostname)
            return
        host = Host(hostname, attrs)
        self.config.append(host)

        print(f"{host}")
        if self.options.get("--yes") or input_is_yes(
            "Do you want to save it", default="n"
        ):
            self.config.write()


class Update(BaseCommand):
    """Update host.

    Usage: update [options] <HOSTNAME> <attribute=value>...

    Arguments:
        HOSTNAME target hostname

    Options:
        -p --use-pattern    Use pattern to find hosts
        -y --yes            Force answer yes
        -v --verbose        Verbose Output
        -h --help           Shwo this screen

    Attributes:
        {% for attr, attr_type in attrs %}
        {{ attr }}
        {% endfor %}
    """
    def pre_command(self):
        template = Template(self.__doc__, trim_blocks=True, lstrip_blocks=True)
        self.__doc__ = template.render(attrs=Host.attrs)

    def execute(self):
        verbose = self.options.get("--verbose")
        hostname = self.options.get("<HOSTNAME>")
        attrs = self.options.get("<attribute=value>", [])
        is_bastion = self.options.get("--bastion")  # TODO
        try:
            attrs = {
                attr.split("=")[0]: attr.split("=")[1]
                for attr in self.options.get("<attribute=value>", [])
            }
        except Exception as e:
            raise Exception(f"<attribute=value> like options aren't provided, {e}, {self.options.get('<attribute=value>')}")
        use_pattern = self.options.get("--use-pattern")
        if use_pattern:
            """ use-pattern is only accept update, not add """
            hosts = [
                host for host in self.config if fnmatch.fnmatch(host.name, hostname)
            ]
            if hosts:
                for host in hosts:
                    self.config.update(host.name, attrs)
                    print(f"{host}")
            else:
                print("No hosts found")
                return
        else:
            host = self.config.get(hostname, raise_exception=False)
            if not host:
                print("No host to be updated, %s" % hostname)
            if verbose:
                print("Update attributes: %s" % attrs)
            self.config.update(hostname, attrs)

        print(f"{host}")
        if self.options.get("--yes") or input_is_yes(
            "Do you want to save it", default="n"
        ):
            self.config.write()


class Rename(BaseCommand):
    """Rename host.

    Usage: rename [options] <OLD_HOSTNAME> <NEW_HOSTNAME>

    Arguments:
        OLD_HOSTNAME NEW_HOSTNAME

    Options:
        -y --yes            Force answer yes
        -h --help           Shwo this screen
    """
    def execute(self):
        old_hostname = self.options.get("<OLD_HOSTNAME>")
        new_hostname = self.options.get("<NEW_HOSTNAME>")
        host = self.config.get(old_hostname, raise_exception=False)
        if not host:
            print(f"No host to be updated, {old_hostname}")
        host.set_name(new_hostname)
        self.config.rename(old_hostname, new_hostname)

        print(f"{host}")
        if self.options.get("--yes") or input_is_yes(
            "Do you want to save it", default="n"
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
            "Do you want to remove %s" % hostname, default="n"
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
            "Do you want to save it", default="n"
        ):
            self.config.write()


class Export(BaseCommand):
    """Export hosts.
    Usage: export [options] ([FORMAT] <file> | [FORMAT] | <file> )

    Options:
        -x                  Export only essential fields
        -g --group GROUP    Name of group
        -c columns          Column names, A comma separted list of field names.
        -h --help           Show this screen
        -v --verbose        Verbose output
        -y --yes            Forcily yes

    Format:
        csv [default]
    """

    def export_csv(self, fields, essential=False):
        """Export csv file
        """
        if essential:
            header = ["HostName", "User", "Port", "IdentityFile"]
        elif fields:
            header = fields
        else:
            header = [attr for attr, attr_type in Host.attrs]

        data = f"{','.join(['Name'] + header)}\n"
        for host in self.config:
            values = [host.name]
            for name in header:
                values.append(host.get(name, ''))
            data += f"{','.join([str(value) for value in values])}\n"
        return data

    def export_ansible(self, group):
        """Export Ansible inventory

        in INI
        jumper ansible_port=5555 ansible_host=192.0.2.50
        in YAML
        hosts:
            jumper:
                ansible_port: 5555
                ansible_host: 192.0.2.50
        """
        data = ""
        if group:
            data += f"[{group}]\n"

        for host in self.config:
            if host.name == "*" or host.HostName is None:
                continue
            line = "{:<20} ansible_host={:<20}".format(host.name, host.HostName)
            if host.User:
                line += " ansible_user={:<10}".format(host.User)
            if host.IdentityFile:
                line += " ansible_ssh_private_key_file={:<20}".format(host.IdentityFile)
            data += f"{line}\n"
        return data

    def execute(self):
        verbose = self.options.get("--verbose")
        essential = self.options.get("-x")
        group = self.options.get("--group")
        fields = self.options.get("-c").split(",") if self.options.get("-c") else []
        outfile = self.options.get("<file>")
        outformat = self.options.get("FORMAT") or "csv"

        if outfile and os.path.exists(outfile):
            print("%s exists." % outfile)
            if not self.options.get("--yes") and not input_is_yes(
                "Do you want to overwrite it", default="n"
            ):
                return

        if outformat == "csv":
            data = self.export_csv(fields, essential)
        elif outformat == "ansible":
            data = self.export_ansible(group)
        if outfile:
            with open(outfile, "w") as f:
                f.write(data)
            return
        print(data)


class Ping(BaseCommand):
    """Send ping to host.

    usage: get [options] [HOST]

    Options:
        -h --help           Show this screen
    """

    def execute(self):
        host = self.options.get("HOST", None)
        if host is None:
            raise ArgumentRequired
        # Print plain
        if platform.system() == 'Windows':
            run(args=['ping', self.config.get(host).HostName])
        else:
            run(args=['ping', '-t', '4', self.config.get(host).HostName])


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
                    "%s has ProxyComamnd, %s" % (host, host.ProxyCommand), default="n"
                ):
                    return
            host.set("ProxyCommand", "ProxyCommand ssh -q -A bastion -W %h:%p")
