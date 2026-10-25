#!/bin/sh

set -ex
#
mkdir -p $HOME/.ssh
chmod 700 $HOME/.ssh
cp /run/rbackup-config/id_ed25519 $HOME/.ssh/id_ed25519
chmod 400 $HOME/.ssh/id_ed25519
touch $HOME/.ssh/known_hosts
chmod 600 $HOME/.ssh/known_hosts
#
rsync --version
RSYNCCMD="rsync --delete --delete-after -HPaxi --exclude /.databackup.lock"
# mirror
# ssh-keyscan -q -t ed25519 cabhs.srv.menoscero.com
echo 'cabhs.srv.menoscero.com ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAILmzIalusC5H6Oq6t365Il6I480x+arNuT4J/nbqjlHh' >> ~/.ssh/known_hosts
ssh rlinfati@cabhs.srv.menoscero.com test -d /DataVolume/DataBackup/backup-kubernetes/
#
while :; do
    state=$(ssh rlinfati@cabhs.srv.menoscero.com '
        L=/DataVolume/DataBackup/.databackup.lock
        if [ ! -e "$L" ]; then echo free
        elif find "$L" -mmin -10 | grep -q .; then echo busy
        else echo stale
        fi')
    [ "$state" = busy ] || break
    echo "[$(date)] databackup running, waiting"
    sleep 600
done
[ "$state" = stale ] && echo "[$(date)] stale databackup lock, ignoring"
#
$RSYNCCMD rlinfati@cabhs.srv.menoscero.com:/DataVolume/DataBackup/ /DataVolume/DataBackup/
#
# eof
