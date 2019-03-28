from .client import SSHConfig, Host, EmptySSHConfig

__version__ = ".".join(map(str, (0, 0, 10)))

__all__ = [EmptySSHConfig, SSHConfig, Host]
