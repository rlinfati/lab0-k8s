#!/bin/sh

set -ex

sudo grubby --update-kernel=ALL --remove-args="rhgb"

sudo dnf config-manager rhel-10-for-x86_64-extensions-rpms --enable
sudo dnf config-manager rhel-10-for-x86_64-supplementary-rpms --enable
#sudo dnf --disablerepo \*  --enablerepo rhel-10-for-x86_64-extensions-rpms list --available
#sudo dnf --disablerepo \*  --enablerepo rhel-10-for-x86_64-supplementary-rpms list --available
# https://developer.download.nvidia.com/compute/cuda/repos/rhel9/x86_64/precompiled/
# https://developer.download.nvidia.com/compute/cuda/repos/rhel10/x86_64

sudo dnf install nvidia-container-toolkit
sudo dnf install nvidia-driver-cuda
# nvidia-driver-cuda # nvidia-smi and libcuda.so
# nvidia-driver      # libEGL, libGLES, libGLX

##########
# reboot #
##########

sudo nvidia-ctk runtime configure --runtime=crio --set-as-default=false --config=/etc/crio/crio.conf.d/99-nvidia.conf
find /etc/crio/
sudo systemctl restart crio

# eof
