#!/bin/sh

set -ex

sudo grubby --update-kernel=ALL --remove-args="rhgb"

sudo dnf config-manager rhel-10-for-x86_64-extensions-rpms --enable
sudo dnf config-manager rhel-10-for-x86_64-supplementary-rpms --enable
#sudo dnf --disablerepo \*  --enablerepo rhel-10-for-x86_64-extensions-rpms list --available
#sudo dnf --disablerepo \*  --enablerepo rhel-10-for-x86_64-supplementary-rpms list --available

sudo dnf config-manager --add-repo https://developer.download.nvidia.com/compute/cuda/repos/rhel10/x86_64/cuda-rhel10.repo
sudo dnf config-manager --setopt=cuda-rhel10-x86_64.priority=999 --save
#sudo dnf --disablerepo \*  --enablerepo cuda-rhel10-x86_64 list --available

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
