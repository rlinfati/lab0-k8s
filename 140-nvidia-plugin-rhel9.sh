#!/bin/sh

set -ex

sudo grubby --update-kernel=ALL --remove-args="rhgb"

sudo dnf config-manager --add-repo https://developer.download.nvidia.com/compute/cuda/repos/rhel9/x86_64/cuda-rhel9.repo
sudo dnf config-manager --setopt=cuda-rhel9-x86_64.priority=999 --save
#sudo dnf --disablerepo \*  --enablerepo cuda-rhel10-x86_64 list --available

sudo dnf install nvidia-container-toolkit
sudo dnf module install nvidia-driver:535 # cuda12
sudo dnf module install nvidia-driver:580 # cuda12

curl -O https://developer.download.nvidia.com/compute/cuda/repos/rhel9/x86_64/NVIDIA2019-public_key.der
sudo mokutil --import NVIDIA2019-public_key.der

##########
# reboot #
##########

sudo nvidia-ctk runtime configure --runtime=crio --set-as-default=false --config=/etc/crio/crio.conf.d/99-nvidia.conf
sudo systemctl restart crio

# eof
