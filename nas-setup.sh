#!/usr/bin/env sh
ansible-playbook nas.yaml -i inventory/nas.yaml -K $@
