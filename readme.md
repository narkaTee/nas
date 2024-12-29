# nas config

# install ansible collections

`ansible-galaxy install -r requirements.yaml`

# crucial ssd firmware update

updates on linux a kind of a hassle. The download is a iso which boots
a linux system that runs the cli command... 🙄

from: https://medium.com/@vdboor/upgrading-crucial-firmware-on-linux-76056254539

1. [download firmware](https://www.crucial.com/support/ssd-support)
2. this:
```shell
mkdir firmware-upgrade && cd firmware-upgrade
mount -o loop WHATEVER.zip /mnt/
gzip -dc /mnt/boot/corepure64.gz | cpio -idm
# the last command probably outputs a few errors

./sbin/msecli -U -v -i ./opt/firmware/ -n /dev/sdX
```

# ZFS

Available properties: https://manpages.debian.org/bookworm/zfsutils-linux/zfsprops.7.en.html


Migration woes:

* `acltype` needs to be set to posix, otherweise migration of the pipxe
  filesystems fail because unsupported acls.

## ZED

sends notifications for relevant zfs events.
Per default it only sends mails to root when a pool in not healthy.

To test the functionality edit `/etc/zfs/zed.d/zed.rc` and enable
verbose `ZED_NOTIFY_VERBOSE=1` and to a scrub `zpool scrub <pool>`.

You should receive a mail about the successful scrub.

## kernel modules/dkms and Secure Boot

To load kernel modules with secure boot enabled the Machine Owner
Key (MOK) dkms uses to sign modules needs to be registered.

The kernel modules build by dkms also need to signed, this seems to be
automatically setup bei debian (bookworm).

```sh
# list enrolled keys
mokutil --list-enrolled

# debian seems to create moks keys in /var/lib/dkms/
# I don't how ho stable this location is and what lifecycle applies to
# this keys. We'll find out over time ;)
sudo mokutil --import /var/lib/dkms/mok.pub
```

The import might fail on older mainboard because the firmware does not
implement all uefi functions for that command to work.
The workararound is to import the key manually in the bios.

Reboot the machine, enter the BIOS setup, use "advanced mode" and
navigate to Boot/SecureBoot/ManageKeys menus.

The key goes in the 'db' repository.
The Menu might be awkwardly structured read carefully what ths yes/no
options will do. On my old asus board "no" is the options to append a
key from a disk.

See also: https://stackoverflow.com/questions/39226185/kernel-module-mokutil-failed-to-enroll-new-keys

# file server

samba with guest/anon access enabled.

## Connection with windows

Windows 11 24H2 comes with new default settings for smb shares.
Authentication without credentials is disabled by default, to enable it
again:

- Edit Group Policy
- Computer Configuration -> Windows Settings -> Security Settings -> Local Policy -> Security Options -> Micropsoft network client: Digitally sign communications (always): Disabled
- Computer Configuration -> Administrative Templates -> Network -> Lanman Workstation -> Enable insecure guest logons: Enabled

In the future authenticated shares might be an option.

# offline backup

Automatically backup to a USB drive when it is connected and send an email notification when backup is complete.

I could to fancy stuff with zfs pools and `zfs send` to build a really efficient backup, but according to "some dudes on the internet"™️ (for example on this [reddit post](https://www.reddit.com/r/zfs/comments/xt2176/zfs_on_usb_external_hdds_good_or_bad_idea/)) that could get flaky when the pool is not unmounted correcly.
Also this is backup is best kept very simple, I want to be able to mount this on basically on any machine and be able to extract files.

## Device setup

Just take whaterver usb device you have lying around, format it with the **linux** filesystem of your choice and get the filesystem uuid with `blkid`.
The backup makes use of hard links to build a incremental backup with rsync. So the filesystem has to support that.

For the detection to properly work the filesystem uuid needs to show up in udev, to double check use `udevadm info --name=/dev/<device>` and look for the `ID_FS_UUID` device property.
Formatting the device itself works flawless 👌🙂

## Concept

I am using a udev rule to trigger a systemd tamplate unit that runs the backup script.
The udev rule are built to only trigger a run when a usb disk with a known fs uuid is connected.
That triggers the start of a systemd one shot unit that runs the bash backup script.

- https://manpages.debian.org/bookworm/udev/udev.7.en.html
- https://manpages.debian.org/bookworm/systemd/systemd.unit.5.en.html (search for template)

The error handling is very basic, the systemd unit enters a failed state if the backup fails and the montoring will catch that and notify me.
This could be improved by sending a email with the unit output. I could use the OnFailure setting that trigger another systemd unit like in this example [here](https://wiki.archlinux.org/title/Systemd/Timers#MAILTO).
But for now this is food enough.

The backup drives are not encrypted, the drives are not going to be carried around a lot so there is no risk of accidential loss.

# offsite backup

The default is to use symmetric encryption. To use asymmetric encryption
see "gpg key setup".

## Tooling

- duplicity
- 1password-cli

## gpg key setup

IF using asymetric encryption a key pair is needed. Setup a key pair
and set `ob_key_id`

### create new key

`gpg --full-generate-key`

To export for save storage

`gpg --armor --export <key id>`
`gpg --armor --export-secret-key <key id>`


### import key from backup

`gpg --import keys.gpg`

with 1password-cli:

`op read 'op://<vault>/<item>/keys.gpg' | gpg --batch --passphrase "$(op read 'op://<vault>/<item>/passphrase')" --import`

make sure to trust the key ultimately with gpg otherwise encryption will fail.

## S3 backend

For the s3 backend to properly work you need a role with the following
definition:
```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "AllowRw",
            "Effect": "Allow",
            "Action": [
                "s3:PutObject",
                "s3:GetObjectAcl",
                "s3:GetObject",
                "s3:ListBucket",
                "s3:DeleteObject",
                "s3:GetBucketAcl",
                "s3:PutObjectAcl"
            ],
            "Resource": [
                "arn:aws:s3:::<bucket>/*",
                "arn:aws:s3:::<bucket>"
            ]
        }
    ]
}
```

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


# nspawn host

prepares the host to host systemd-nspawn containers and bootstraps
containers.

## tooling

- systemd-container
- debootstrap

## docs

- https://www.freedesktop.org/software/systemd/man/latest/systemd-nspawn.html
- https://www.freedesktop.org/software/systemd/man/latest/systemd.nspawn.html

# nspawn container connection

The become plugin is not usefull for containers because you need to mound
the current users home directory into the container to access the python
scripts ansible creates in the tmp diretory.

see: https://github.com/ansible/ansible/issues/58962

There is a working scetch of a connection plugin:
https://github.com/tomeon/ansible-connection-machinectl

For now I just copied it and simplified it a bit.

# role: nftables

systemd nspawn creates and updates two tables (`io.systemd.nat` ip und ip6)
where is creates rules needed for the container network connections.
It also manages the port forwards there.

When managing our rules we need to make sure not to flush the ruleset
in our nft config files.
We need to make sure we just delete the tables we want to manage.
It also means when removing tables we have to manually clean up the
rules!

# Grafana + Prometheus

- https://github.com/grafana/grafana-ansible-collection/tree/main/roles/grafana
- https://grafana.com/tutorials/run-grafana-behind-a-proxy/
- https://github.com/prometheus-community/ansible
- https://github.com/prometheus-community/ansible/tree/main/roles/prometheus
- https://github.com/prometheus-community/ansible/tree/main/roles/blackbox_exporter
- https://github.com/prometheus-community/ansible/tree/main/roles/alertmanager

## Node Exporter

The `prometheus-node-exporter` package automatically installs and
configures the textfile exporter from the [prometheus-community](https://github.com/prometheus-community/node-exporter-textfile-collector-scripts).

The textfile collector folder is: `/var/lib/prometheus/node-exporter`

### SMART

Useful dashboards:

- https://grafana.com/grafana/dashboards/10664-smart-disk-data/ (removing the extended labels from the queries 👌)
- https://grafana.com/grafana/dashboards/3992-smartmon/ just raw data

# Fritz!Exporter

- https://github.com/pdreker/fritz_exporter
- https://grafana.com/grafana/dashboards/13983-fritz-exporter/
- https://grafana.com/grafana/dashboards/17751-fritz-exporter-dash/
