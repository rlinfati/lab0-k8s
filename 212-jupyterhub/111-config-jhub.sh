#!/bin/sh

set -ex

# lab0arm.m0.cl
ssh clval.vps.menoscero.com "kubectl -n jupyterhub patch configmap jhub.profiles --type merge -p '{\"data\": {\"burstable_1cpu_7gb\":  \"# burstable_1cpu_7gb\"}}'"

# lab0x86.m0.cl
ssh cabhs.srv.menoscero.com "kubectl -n jupyterhub patch configmap jhub.profiles --type merge -p '{\"data\": {\"burstable_1cpu_7gb\":  \"# burstable_1cpu_7gb\"}}'"

# lab017a.m0.cl
ssh cosyn.ubb.menoscero.com "kubectl -n jupyterhub patch configmap jhub.profiles --type merge -p '{\"data\": {\"burstable_1cpu_7gb\":  \"# burstable_1cpu_7gb\"}}'"
ssh cosyn.ubb.menoscero.com "kubectl -n jupyterhub patch configmap jhub.profiles --type merge -p '{\"data\": {\"burstable_4cpu_30gb\": \"# burstable_4cpu_30gb\"}}'"

# lab023a.m0.cl
ssh synco.ubb.menoscero.com "kubectl -n jupyterhub patch configmap jhub.profiles --type merge -p '{\"data\": {\"burstable_1cpu_7gb\":    \"# burstable_1cpu_7gb\"}}'"
ssh synco.ubb.menoscero.com "kubectl -n jupyterhub patch configmap jhub.profiles --type merge -p '{\"data\": {\"burstable_4cpu_30gb\":   \"# burstable_4cpu_30gb\"}}'"
ssh synco.ubb.menoscero.com "kubectl -n jupyterhub patch configmap jhub.profiles --type merge -p '{\"data\": {\"burstable_12cpu_120gb\": \"# burstable_12cpu_120gb\"}}'"

# reset
kubectl -n jupyterhub delete pod --all

# eof
