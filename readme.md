# Host Setup

Started as a repo for my nas. Morphed into a repo for multiple hosts 🤷

# Pre Requisites

```bash
uv run ansible-galaxy install -r requirements.yaml
```

# Hosts

## Nas

**Provision locally!**

Fileshare backups and various services in nspawn containers.

see [nas](docs/nas.md)

## ha-host

**Provision locally in tmux!** Bride setup could interfere with the ssh connection.

Debian machine running a VM for home assiatant.

Why the heck not bare-metal? Because I want to be able to properly monitor the hardware with node exporter
and do other linux stuff!
