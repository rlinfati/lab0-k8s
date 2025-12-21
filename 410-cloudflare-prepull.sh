#!/bin/sh

set -ex

sudo podman image prune --force
sudo podman image ls -a | sort

sudo podman pull --quiet docker.io/cloudflare/cloudflared:latest
sudo podman image prune --force

sudo podman image prune --force
sudo podman image ls -a | sort

# eof
