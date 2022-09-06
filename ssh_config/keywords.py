def yes_or_no(value: str) -> bool:
    """Convert 'yes' or 'no' to True or False
    Args:
        value (str): The string containing 'yes' or 'no'
    Returns:
        bool: True if value is 'yes', False if value is 'no'
    """
    if value is None:
        return
    if value.lower() not in ('yes', 'no'):
        raise TypeError("Yes or No is required")
    convert = {
        "yes": True,
        "no": False
    }
    return convert[value.lower()]


def yes_or_no_str(value: bool) -> str:
    """Convert True or False to 'yes' or 'no'
    Args:
        value (bool): True/False
    Returns:
        str: 'yes' if value is True, 'no' if value is False/None
    """
    if value is None:
        return "no"
    return "yes" if value else "no"


class Keyword:
    def __init__(self, key: str, type_converter: type,
                 persist_converter: type = None) -> None:
        self.key = key
        self.type_converter = type_converter
        self.persist_converter = persist_converter if persist_converter else type_converter


Keywords = [
    Keyword("HostName", str),
    Keyword("User", str),
    Keyword("Port", int),
    Keyword("IdentityFile", str),
    Keyword("AddressFamily", str),  # any, inet, inet6
    Keyword("BatchMode", str),
    Keyword("BindAddress", str),
    Keyword("ChallengeResponseAuthentication", str),  # yes, no
    Keyword("CheckHostIP", str),  # yes, no
    Keyword("Cipher", str),
    Keyword("Ciphers", str),
    Keyword("ClearAllForwardings", str),  # yes, no
    Keyword("Compression", str),  # yes, no
    Keyword("CompressionLevel", int),  # 1 to 9
    Keyword("ConnectionAttempts", int),  # default: 1
    Keyword("ConnectTimeout", int),
    Keyword("ControlMaster", str),  # yes, no
    Keyword("ControlPath", str),
    Keyword("DynamicForward", str),  # [bind_address:]port, [bind_adderss/]port
    Keyword("EnableSSHKeysign", str),  # yes, no
    Keyword("EscapeChar", str),  # default: '~'
    Keyword("ExitOnForwardFailure", str),  # yes, no
    Keyword("ForwardAgent", str),  # yes, no
    Keyword("ForwardX11", str),  # yes, no
    Keyword("ForwardX11Trusted", str),  # yes, no
    Keyword("GatewayPorts", str),  # yes, no
    Keyword("GlobalKnownHostsFile", str),  # yes, no
    Keyword("GSSAPIAuthentication", str),  # yes, no
    Keyword("LocalCommand", str),
    Keyword("LocalForward", str),
    Keyword("LogLevel", str),
    Keyword("ProxyCommand", str),
    Keyword("ProxyJump", str),
    Keyword("Match", str),
    Keyword("AddKeysToAgent", str),
    Keyword("BindInterface", str),
    Keyword("CanonicalizeHostname", str),  # yes, no
    Keyword("CanonicalizeMaxDots", int),
    Keyword("CanonicalDomains", str),
    Keyword("CanonicalizePermittedCNAMEs", str),
    Keyword("CanonicalizeFallbackLocal", str),
    Keyword("IdentityAgent", str),
    Keyword("PreferredAuthentications", str),
    Keyword("ServerAliveInterval", int),
    Keyword("ServerAliveCountMax", int),
    Keyword("UsePrivilegedPort", str),  # yes, no
    Keyword("TCPKeepAlive", str),  # yes, no
    Keyword("Include", str),
    Keyword("IPQoS", str),
    Keyword("GlobalKnownHostsFile", str),
    Keyword("UserKnownHostsFile", str),
    Keyword("GSSAPIDelegateCredentials", str),
    Keyword("PKCS11Provider", str),
    Keyword("XAuthLocation", str),
    Keyword("PasswordAuthentication", yes_or_no, yes_or_no_str),  # default: yes
    Keyword("KbdInteractiveAuthentication", str),
    Keyword("KbdInteractiveDevices", str),
    Keyword("PubkeyAuthentication", str),
    Keyword("HostbasedAuthentication", str),
    Keyword("IdentitiesOnly", yes_or_no, yes_or_no_str),  # default: no
    Keyword("CertificateFile", str),
    Keyword("HostKeyAlias", str),
    Keyword("MACs", str),
    Keyword("RemoteForward", str),
    Keyword("PermitRemoteOpen", str),
    Keyword("StrictHostKeyChecking", yes_or_no, yes_or_no_str),
    Keyword("NumberOfPasswordPrompts", str),
    Keyword("SyslogFacility", str),
    Keyword("LogVerbose", str),
    Keyword("HostKeyAlgorithms", str),
    Keyword("CASignatureAlgorithms", str),
    Keyword("VerifyHostKeyDNS", str),
    Keyword("NoHostAuthenticationForLocalhost", str),
    Keyword("RekeyLimit", str),
    Keyword("SendEnv", str),
    Keyword("SetEnv", str),
    Keyword("ControlPersist", str),
    Keyword("HashKnownHosts", str),
    Keyword("Tunnel", str),
    Keyword("TunnelDevice", str),
    Keyword("PermitLocalCommand", str),
    Keyword("RemoteCommand", str),
    Keyword("VisualHostKey", str),
    Keyword("KexAlgorithms", str),
    Keyword("RequestTTY", str),
    Keyword("SessionType", str),
    Keyword("StdinNull", str),
    Keyword("ForkAfterAuthentication", str),
    Keyword("ProxyUseFdpass", str),
    Keyword("StreamLocalBindMask", str),
    Keyword("StreamLocalBindUnlink", str),
    Keyword("RevokedHostKeys", str),
    Keyword("FingerprintHash", str),  # md5 or sha256
    Keyword("UpdateHostKeys", str),
    Keyword("HostbasedAcceptedAlgorithms", str),
    Keyword("PubkeyAcceptedAlgorithms", str),
    Keyword("IgnoreUnknown", str),
    Keyword("SecurityKeyProvider", str),
    Keyword("KnownHostsCommand", str),
]
