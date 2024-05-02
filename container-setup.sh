#!/usr/bin/env sh
# this is is a little trick to pass $@ to the sh command run by sudo.
# we need to pass additional arguments everything we just pass additional
# parameters to sh -c ''
sudo -- sh -c '. $HOME/.config/env.local.sh && ansible-playbook containers.yaml $@' sh "$@"
