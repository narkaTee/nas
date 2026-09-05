# Home Assistant VM

The libvirt domain is named `home-assistant`. Run these commands on `ha-host`.

## Status

```bash
sudo virsh list --all
sudo virsh dominfo home-assistant
sudo virsh domstate home-assistant
```

Show its network interface and addresses reported by the guest agent:

```bash
sudo virsh domiflist home-assistant
sudo virsh domifaddr home-assistant --source agent
```

Use the host's ARP table as a fallback if the guest agent is unavailable:

```bash
sudo virsh domifaddr home-assistant --source arp
```

## Troubleshooting

Check that libvirt and the QEMU guest agent respond:

```bash
sudo systemctl status libvirtd
sudo virsh qemu-agent-command home-assistant '{"execute":"guest-ping"}'
```

Show recent libvirt logs:

```bash
sudo journalctl --unit libvirtd --since today
sudo journalctl --unit libvirtd --follow
```

Show attached disks, network interfaces, and USB devices:

```bash
sudo virsh domblklist home-assistant --details
sudo virsh domiflist home-assistant
sudo virsh dumpxml home-assistant | less
```

## Restart

Request a graceful reboot through the QEMU guest agent:

```bash
sudo virsh reboot home-assistant --mode agent
```

If a normal reboot does not work, request a graceful shutdown and start the VM
again after it has stopped:

```bash
sudo virsh shutdown home-assistant --mode agent
sudo virsh domstate home-assistant
sudo virsh start home-assistant
```

As a last resort, perform the equivalent of pulling the power and start the VM
again:

```bash
sudo virsh destroy home-assistant
sudo virsh start home-assistant
```

`destroy` does not delete the VM or its disk, but the forced power-off can cause
data loss. Use it only when the guest no longer responds.

## Configuration

Display the persistent configuration managed by Ansible:

```bash
sudo virsh dumpxml --inactive home-assistant | less
```

Make persistent CPU, memory, disk, network, or USB passthrough changes in
`inventory/host_vars/ha-host.yaml`, then apply them with:

```bash
./setup ha-host
```

Changes to a running VM may require a restart before they become active.
