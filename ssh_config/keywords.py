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
]
