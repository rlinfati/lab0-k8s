#!/bin/sh

set -ex

sudo kubeadm reset --cleanup-tmp-dir
rm -r $HOME/.kube

sudo podman image prune --all
sudo podman system prune --all
sudo podman system reset --force
sudo podman image ls -a
sudo kubeadm config images pull

# eof
