#!/usr/bin/env sh
uv run ansible-playbook hosts.yaml -K $@
