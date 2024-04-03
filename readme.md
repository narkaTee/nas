# nas config

# raspberry pi pxe boot

**There is basically NO security for the nfs shares! Consider them
public in the local network**

Docs:

- https://www.raspberrypi.com/documentation/computers/raspberry-pi.html#network-booting
- https://www.raspberrypi.com/documentation/computers/configuration.html#the-kernel-command-line
- losely based on: https://hackaday.com/2018/10/08/hack-my-house-running-raspberry-pi-without-an-sd-card/
- kernel params: https://www.kernel.org/doc/html/latest/admin-guide/nfs/nfsroot.html

## Nice to know

- tcp ist most stable between various kernels (I ran some REAL old ones
  and without explicitly setting the tcp option the nfs connection would
  experience dropouts)
- older kernels can't handle nfs v4 correcly, v3 works.

## Preparations

.cache/pi.img should be a raspberry pi os image. The bootstrapping
process depends on the partition layout on the image.

https://www.raspberrypi.com/software/operating-systems/#raspberry-pi-os-64-bit

## Components

- dnsmasq
  - dhcp proxy to reply with the pxe and tftp settings
  - tftpserver to host bootcode and pxe loader
- nfs-kernel-server
  - nfs server to host the root and boot folders which will be mounted by the pi
