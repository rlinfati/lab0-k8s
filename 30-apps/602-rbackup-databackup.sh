#!/bin/sh

set -ex
#
test -d /DataVolume/DataBackup/backup-kubernetes/
#
LOCK=/DataVolume/DataBackup/.databackup.lock
touch "$LOCK"
(
    set +x
    while :; do
        sleep 60
        touch "$LOCK"
    done
) &
HEARTBEAT=$!
trap 'kill "$HEARTBEAT" || true; rm -f "$LOCK"' EXIT
trap 'exit 1' TERM INT
#
mkdir -p $HOME/.config/rclone/
cp /run/rbackup-config/rclone.conf $HOME/.config/rclone/rclone.conf
#
rclone version
# DeDupe
rclone --dry-run dedupe gdrive:
rclone --dry-run dedupe linfati-gdrive:
rclone --dry-run dedupe linfati-rlshared:
rclone --dry-run dedupe ubiobio:
# Rescue Orphans
rclone backend rescue gdrive:
rclone backend rescue linfati-gdrive:
rclone backend rescue linfati-rlshared:
rclone backend rescue ubiobio:
# -> RodrigoLinfatiShared
rclone sync dropbox:          linfati-rlshared:mirror-dropbox/
rclone sync gdrive:           linfati-rlshared:mirror-gdrive/
rclone sync linfati-gdrive:   linfati-rlshared:mirror-linfati-gdrive/
rclone sync onedrive:         linfati-rlshared:mirror-onedrive/
rclone sync ubiobio:          linfati-rlshared:mirror-ubiobio-gdrive/ --exclude rlinfati-vscam/
rclone sync ubiobio-ms:       linfati-rlshared:mirror-ubiobio-onedrive/
# RodrigoLinfatiShared -> DataBackup
rclone sync linfati-rlshared:backup-kubernetes/ /DataVolume/DataBackup/backup-kubernetes/
rclone sync linfati-rlshared:backup-fotos/      /DataVolume/DataBackup/backup-fotos/
rclone sync linfati-rlshared:home-rlinfati/     /DataVolume/DataBackup/home-rlinfati/
rclone sync dropbox:                            /DataVolume/DataBackup/mirror-dropbox/
rclone sync gdrive:                             /DataVolume/DataBackup/mirror-gdrive/
rclone sync linfati-gdrive:                     /DataVolume/DataBackup/mirror-linfati-gdrive/
rclone sync onedrive:                           /DataVolume/DataBackup/mirror-onedrive/
rclone sync ubiobio:                            /DataVolume/DataBackup/mirror-ubiobio-gdrive/ --exclude rlinfati-vscam/
rclone sync ubiobio-ms:                         /DataVolume/DataBackup/mirror-ubiobio-onedrive/
rclone sync linfati-rlshared:                   /DataVolume/DataBackup/ --no-update-modtime --no-update-dir-modtime --dry-run # dry-run
#
mkdir -p $HOME/.ssh
chmod 700 $HOME/.ssh
cp /run/rbackup-config/id_ed25519 $HOME/.ssh/id_ed25519
chmod 400 $HOME/.ssh/id_ed25519
touch $HOME/.ssh/known_hosts
chmod 600 $HOME/.ssh/known_hosts
#
rsync --version
#
RSYNCCMD="rsync --delete --delete-after -HPaxi --exclude /.databackup.lock"
#
# DataBackup -> Hetzner
# ssh-keyscan -q -t ed25519 -p 23 u190950.your-storagebox.de
echo '[u190950.your-storagebox.de]:23 ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIICf9svRenC/PLKIL9nk6K/pxQgoiFC41wTNvoIncOxs' >> ~/.ssh/known_hosts
$RSYNCCMD -e 'ssh -p 23 -l u190950' /DataVolume/DataBackup/ u190950.your-storagebox.de:/home/DataBackup/
#
# DataBackup -> rsync.net
# ssh-keyscan -q -t ed25519 de4108.rsync.net
echo 'de4108.rsync.net ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIObQN4P/deJ/k4P4kXh6a9K4Q89qdyywYetp9h3nwfPo' >> ~/.ssh/known_hosts
$RSYNCCMD /DataVolume/DataBackup/ de4108@de4108.rsync.net:DataBackup/
#
# eof
