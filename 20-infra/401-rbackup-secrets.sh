#!/bin/sh

set -ex

kubectl -n rbackup create secret generic config \
  --from-file=id_ed25519="$HOME/.ssh/id_MacBookPro2020" \
  --from-file=rclone.conf="$HOME/.config/rclone/rclone.conf" \
  --dry-run=client -o yaml |
tee 20-infra/401-rbackup-secrets.yaml

# eof
