~/.ssh/config
=============
http://man.openbsd.org/ssh_config.5

* Host
* Match
* AddKeysToAgent
* AddressFamily
* BatchMode
* BindAddress
* BindInterface
* CanonialDomains
* CnonicalizeFallbackLocal
* IdentityAgent
* IdentityFile
* LocalCommand
* LocalForward
* LogLevel
* Port
* PreferredAuthentications
* ProxyCommand
* User

Example::
   Host server1
      ServerAliveInterval 200
      HostName 203.0.113.76
   Host * 
      ExitOnForwardFailure yes
      Protocol 2
      ServerAliveInterval 400


~/.ssh/known_hosts
==================

exmaple1::
   host,ip ssh-rsa AAAA...njvPw==
   host ssh-rsa AAAAB3Nz...cTgsdfjflsf==


example2::
   [ssh.example.org]:2222 ssh-rsa AAAAANz....lfdjs=
   [anga.funkfeuer.at]:2022,[78.31.114.3]:2022 ssh-rsa AAAAB...sfjslfs=
