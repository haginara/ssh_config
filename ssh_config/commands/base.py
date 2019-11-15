import docopt
import inspect


class NoDocExit(Exception):
    pass


class ArgumentRequired(Exception):
    pass


class NoExistCommand(Exception):
    def __init__(self, command, supercommand):
        super().__init__("No Exist Command: %s" % command)

        self.command = command
        self.supercommand = supercommand


class BaseCommand(object):
    """Base class for Command"""

    def __init__(self, config, options, g_options, options_first=False):
        if not self.__doc__:
            raise NoDocExist
        self.config = config
        self.options = docopt.docopt(
            self.__doc__, argv=options, options_first=options_first
        )
        self.g_options = g_options

    def execute(self):
        """Execute Command"""
        raise NotImplementedError


class NestCommand(BaseCommand):
    """NestCommand"""

    def __init__(self, config, options, g_options, options_first=True):
        super().__init__(config, options, g_options, options_first)

    def execute(self):
        command_name = self.options.pop("<command>")

        # Retrieve the command arguments.
        command_args = self.options.pop("<args>")
        if command_args is None:
            command_args = {}

        # Retrieve the class from the 'commands' module.
        try:
            command_func = getattr(self, command_name)
        except AttributeError:
            print(f"Unknown command. {command_name}.")
            raise docopt.DocoptExit()

        cmd_docstring = inspect.getdoc(command_func)
        command_options = docopt.docopt(
            cmd_docstring, argv=command_args, options_first=False
        )
        # Execute the command.
        print("Execute the command")
        command_func(command_options)
