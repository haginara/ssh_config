
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
        "no": False,
        True: "yes",
        False: "no",
    }
    return convert[value]


Keywords = [
    ("HostName", str),
    ("User", str),
    ("Port", int),
    ("IdentityFile", str),
    ("AddressFamily", str),  # any, inet, inet6
    ("BatchMode", str),
    ("BindAddress", str),
    ("ChallengeResponseAuthentication", str),  # yes, no
    ("CheckHostIP", str),  # yes, no
    ("Cipher", str),
    ("Ciphers", str),
    ("ClearAllForwardings", str),  # yes, no
    ("Compression", str),  # yes, no
    ("CompressionLevel", int),  # 1 to 9
    ("ConnectionAttempts", int),  # default: 1
    ("ConnectTimeout", int),
    ("ControlMaster", str),  # yes, no
    ("ControlPath", str),
    ("DynamicForward", str),  # [bind_address:]port, [bind_adderss/]port
    ("EnableSSHKeysign", str),  # yes, no
    ("EscapeChar", str),  # default: '~'
    ("ExitOnForwardFailure", str),  # yes, no
    ("ForwardAgent", str),  # yes, no
    ("ForwardX11", str),  # yes, no
    ("ForwardX11Trusted", str),  # yes, no
    ("GatewayPorts", str),  # yes, no
    ("GlobalKnownHostsFile", str),  # yes, no
    ("GSSAPIAuthentication", str),  # yes, no
    ("LocalCommand", str),
    ("LocalForward", str),
    ("LogLevel", str),
    ("ProxyCommand", str),
    ("ProxyJump", str),
    ("Match", str),
    ("AddKeysToAgent", str),
    ("BindInterface", str),
    ("CanonicalizeHostname", str),  # yes, no
    ("CanonicalizeMaxDots", int),
    ("CanonicalDomains", str),
    ("CanonicalizePermittedCNAMEs", str),
    ("CanonicalizeFallbackLocal", str),
    ("IdentityAgent", str),
    ("PreferredAuthentications", str),
    ("ServerAliveInterval", int),
    ("ServerAliveCountMax", int),
    ("UsePrivilegedPort", str),  # yes, no
    ("TCPKeepAlive", str),  # yes, no
    ("Include", str),
    ("IPQoS", str),
    ("GlobalKnownHostsFile", str),
    ("UserKnownHostsFile", str),
    ("GSSAPIDelegateCredentials", str),
    ("PKCS11Provider", str),
    ("XAuthLocation", str),
    ("PasswordAuthentication", yes_or_no),  # default: yes
    ("KbdInteractiveAuthentication", str),
    ("KbdInteractiveDevices", str),
    ("PubkeyAuthentication", str),
    ("HostbasedAuthentication", str),
    ("IdentitiesOnly", yes_or_no),  # default: no
    ("CertificateFile", str),
    ("HostKeyAlias", str),
    ("MACs", str),
    ("RemoteForward", str),
    ("PermitRemoteOpen", str),
    ("StrictHostKeyChecking", yes_or_no),
    ("NumberOfPasswordPrompts", str),
    ("SyslogFacility", str),
    ("LogVerbose", str),
    ("HostKeyAlgorithms", str),
    ("CASignatureAlgorithms", str),
    ("VerifyHostKeyDNS", str),
    ("NoHostAuthenticationForLocalhost", str),
    ("RekeyLimit", str),
    ("SendEnv", str),
    ("SetEnv", str),
    ("ControlPersist", str),
    ("HashKnownHosts", str),
    ("Tunnel", str),
    ("TunnelDevice", str),
    ("PermitLocalCommand", str),
    ("RemoteCommand", str),
    ("VisualHostKey", str),
    ("KexAlgorithms", str),
    ("RequestTTY", str),
    ("SessionType", str),
    ("StdinNull", str),
    ("ForkAfterAuthentication", str),
    ("ProxyUseFdpass", str),
    ("StreamLocalBindMask", str),
    ("StreamLocalBindUnlink", str),
    ("RevokedHostKeys", str),
    ("FingerprintHash", str),  # md5 or sha256
    ("UpdateHostKeys", str),
    ("HostbasedAcceptedAlgorithms", str),
    ("PubkeyAcceptedAlgorithms", str),
    ("IgnoreUnknown", str),
    ("SecurityKeyProvider", str),
    ("KnownHostsCommand", str),
]
