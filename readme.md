# nas config

# install dependencies

`ansible-galaxy install -r requirements.yaml`

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
