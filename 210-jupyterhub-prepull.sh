#!/bin/sh

set -ex

sudo podman image prune --force
sudo podman image ls -a | sort

sudo podman pull --quiet ghcr.io/rlinfati/lab0-container:jupyter-hub
sudo podman pull --quiet ghcr.io/rlinfati/lab0-container:jupyter-lab-julia-1.13
sudo podman pull --quiet ghcr.io/rlinfati/lab0-container:jupyter-lab-julia-1.12
sudo podman pull --quiet ghcr.io/rlinfati/lab0-container:jupyter-lab-julia-1.10
sudo podman pull --quiet ghcr.io/rlinfati/lab0-container:jupyter-lab-anaconda-latest
sudo podman pull --quiet ghcr.io/rlinfati/lab0-container:jupyter-lab-devcpp-latest
sudo podman pull --quiet ghcr.io/rlinfati/lab0-container:jupyter-lab-base-latest
sudo podman image prune --force

if [[ -c /dev/nvidiactl ]]; then
    sudo podman pull --quiet ghcr.io/rlinfati/lab0-container:jupyter-lab-juliacuda-1.12
    sudo podman pull --quiet ghcr.io/rlinfati/lab0-container:jupyter-nvcr-pytorch
    sudo podman pull --quiet quay.io/jupyter/pytorch-notebook:cuda12-latest
    sudo podman pull --quiet quay.io/jupyter/tensorflow-notebook:cuda-latest
    sudo podman image prune --force
fi

sudo podman pull --quiet quay.io/jupyter/julia-notebook:latest
sudo podman pull --quiet quay.io/jupyter/scipy-notebook:latest
sudo podman pull --quiet quay.io/jupyter/r-notebook:latest
sudo podman pull --quiet quay.io/jupyter/pytorch-notebook:latest
sudo podman pull --quiet quay.io/jupyter/tensorflow-notebook:latest
sudo podman image prune --force

sudo podman image prune --force
sudo podman image ls -a | sort

# eof
