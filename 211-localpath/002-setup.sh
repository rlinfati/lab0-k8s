#!/bin/sh

set -ex

sudo mkdir --context=unconfined_u:object_r:container_file_t:s0 /home/localpath

# eof
