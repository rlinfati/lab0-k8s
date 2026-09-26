#!/bin/sh

set -ex

sudo mkdir --context=system_u:object_r:mnt_t:s0 /var/mnt
sudo mkdir --context=system_u:object_r:container_file_t:s0 /var/mnt/localpath

sudo semanage fcontext -Cl
sudo semanage fcontext -l | grep local-path-provisioner
sudo semanage fcontext -a -e /opt/local-path-provisioner /mnt/localpath
sudo restorecon -nvR /var/mnt/localpath

# eof
