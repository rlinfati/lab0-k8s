#!/bin/sh

set -ex

sudo mkdir --context=system_u:object_r:container_ro_file_t:s0 /var/lib/containers/imagestore/

sudo semanage fcontext -Cl
sudo semanage fcontext -l | grep var.lib.containers
sudo semanage fcontext -a -e /var/lib/containers/storage /var/lib/containers/imagestore
sudo restorecon -nvR /var/lib/containers/imagestore

sudo tee /etc/containers/storage.conf >/dev/null <<EOF
[storage]
imagestore = "/var/lib/containers/imagestore"
EOF

sudo systemctl restart crio

# eof
