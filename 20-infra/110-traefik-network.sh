#!/bin/sh

set -ex

sudo firewall-cmd --permanent --zone=public --add-service=http --add-service=https
sudo firewall-cmd             --zone=public --add-service=http --add-service=https
sudo firewall-cmd --zone=public --list-all

# eof
