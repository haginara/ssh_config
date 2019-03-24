from .client import SSHConfig, Host, EmptySSHConfig

__version__ = ".".join(map(str, (0, 0, 9)))

__all__ = [EmptySSHConfig, SSHConfig, Host]
