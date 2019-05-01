# ipxe.efi

A default build of https://ipxe.org with a embeded boot script of:

```
#!ipxe

set next-server-port 80

dhcp &&
chain http://${next-server}:${next-server-port}/default.ipxe
```

Where `${next-server}` will be whatever the DHCP option are set to.