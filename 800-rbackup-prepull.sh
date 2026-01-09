#!/bin/sh

set -ex

sudo podman image prune --force
sudo podman image ls -a | sort

sudo podman pull --quiet ghcr.io/rlinfati/lab0-container:rbackup
sudo podman image prune --force

sudo podman image prune --force
sudo podman image ls -a | sort

# eof
