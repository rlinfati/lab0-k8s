#!/bin/sh

set -ex

ssh cabhs.srv.menoscero.com kubectl apply -f - < 841-prepull-network.yaml
ssh cabhs.srv.menoscero.com kubectl apply -f - < 842-prepull-jupyter.yaml
echo ssh cabhs.srv.menoscero.com kubectl apply -f - < 843-prepull-jupytercuda.yaml
ssh cabhs.srv.menoscero.com kubectl apply -f - < 844-prepull-infra.yaml

ssh clval.vps.menoscero.com kubectl apply -f - < 841-prepull-network.yaml
ssh clval.vps.menoscero.com kubectl apply -f - < 842-prepull-jupyter.yaml
echo ssh clval.vps.menoscero.com kubectl apply -f - < 843-prepull-jupytercuda.yaml
ssh clval.vps.menoscero.com kubectl apply -f - < 844-prepull-infra.yaml

ssh fenix.ubb.menoscero.com kubectl apply -f - < 841-prepull-network.yaml
ssh fenix.ubb.menoscero.com kubectl apply -f - < 842-prepull-jupyter.yaml
echo ssh fenix.ubb.menoscero.com kubectl apply -f - < 843-prepull-jupytercuda.yaml
ssh fenix.ubb.menoscero.com kubectl apply -f - < 844-prepull-infra.yaml

ssh radio.ubb.menoscero.com kubectl apply -f - < 841-prepull-network.yaml
ssh radio.ubb.menoscero.com kubectl apply -f - < 842-prepull-jupyter.yaml
ssh radio.ubb.menoscero.com kubectl apply -f - < 843-prepull-jupytercuda.yaml
ssh radio.ubb.menoscero.com kubectl apply -f - < 844-prepull-infra.yaml

ssh reloj.ubb.menoscero.com kubectl apply -f - < 841-prepull-network.yaml
ssh reloj.ubb.menoscero.com kubectl apply -f - < 842-prepull-jupyter.yaml
ssh reloj.ubb.menoscero.com kubectl apply -f - < 843-prepull-jupytercuda.yaml
ssh reloj.ubb.menoscero.com kubectl apply -f - < 844-prepull-infra.yaml

# clean up old images

ssh cabhs.srv.menoscero.com sudo podman image prune --force
ssh clval.vps.menoscero.com sudo podman image prune --force
ssh fenix.ubb.menoscero.com sudo podman image prune --force
ssh radio.ubb.menoscero.com sudo podman image prune --force
ssh reloj.ubb.menoscero.com sudo podman image prune --force

ssh cabhs.srv.menoscero.com sudo podman image ls -a | sort
ssh clval.vps.menoscero.com sudo podman image ls -a | sort
ssh fenix.ubb.menoscero.com sudo podman image ls -a | sort
ssh radio.ubb.menoscero.com sudo podman image ls -a | sort
ssh reloj.ubb.menoscero.com sudo podman image ls -a | sort

# eof
