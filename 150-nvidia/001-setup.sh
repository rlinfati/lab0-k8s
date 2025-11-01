#!/bin/sh

set -ex

sudo grubby --update-kernel=ALL --remove-args="rhgb"
sudo dnf config-manager --add-repo https://developer.download.nvidia.com/compute/cuda/repos/rhel9/x86_64/cuda-rhel9.repo
sudo dnf config-manager --add-repo https://developer.download.nvidia.com/hpc-sdk/rhel/nvhpc.repo

sudo dnf install nvidia-container-toolkit
sudo dnf module install nvidia-driver:535

curl -O https://developer.download.nvidia.com/compute/cuda/repos/rhel9/x86_64/NVIDIA2019-public_key.der
sudo mokutil --import NVIDIA2019-public_key.der

##########
# reboot #
##########

sudo nvidia-ctk cdi generate --output=/etc/cdi/nvidia.yaml
sudo nvidia-ctk runtime configure --runtime=crio --set-as-default=false --config=/etc/crio/crio.conf.d/99-nvidia.conf
sudo systemctl restart crio

#  OK RUNC + LEGACY
# NOK CRUN + CDI
sudo ln -s /usr/libexec/crio/runc /usr/local/sbin/

# eof
