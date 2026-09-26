#!/bin/sh

set -ex

kubectl get node --show-labels | sed s/\,/\\n/g

kubectl label nodes $(hostname --long) node-role.kubernetes.io/control-plane=

kubectl label nodes $(hostname --long) nvidia.com/gpu.present=true
kubectl label nodes $(hostname --long) m0net/infralab=true
kubectl taint nodes $(hostname --long) m0net/infralab:PreferNoSchedule

kubectl label nodes $(hostname --long) m0net/run.rbackup=databackup
kubectl label nodes $(hostname --long) m0net/run.rbackup=mirror
kubectl label nodes $(hostname --long) m0net/run.rec4cam=true
kubectl label nodes $(hostname --long) m0net/run.yfinance=true

kubectl label nodes $(hostname --long) m0net/run.cloudflared=true
kubectl label nodes $(hostname --long) m0net/run.tailscale=true
kubectl label nodes $(hostname --long) m0net/run.strongswan=true
kubectl label nodes $(hostname --long) m0net/run.grbts=true
kubectl label nodes $(hostname --long) m0net/run.vlmcsd=true

kubectl label nodes $(hostname --long) m0net/run.jupyterhub=true
kubectl label nodes $(hostname --long) m0net/run.jupyterlab=true

# eof

#                                 nuc4x clval cabhs fenix radio reloj
# nvidia.com/gpu.present=true                               x     x
# m0net/infralab=true               x     x     x     x     x     x
# m0net/run.rbackup=databackup                  x
# m0net/run.rbackup=mirror                            x     x     x
# m0net/run.rec4cam=true            x
# m0net/run.yfinance=true           x           x
# m0net/run.cloudflared=true        x
# m0net/run.tailscale=true          x
# m0net/run.strongswan=true               x     x     x
# m0net/run.grbts=true                    x     x     x     x     x
# m0net/run.vlmcsd=true                   x     x     x     x     x
# m0net/run.jupyterhub=true               x     x     x     x     x
# m0net/run.jupyterlab=true               x     x     x     x     x

# kubectl taint nodes rpi5-7f7afe node-role.kubernetes.io/control-plane:NoSchedule
# kubectl label nodes rpi5-7f7afe node-role.kubernetes.io/control-plane=

# kubectl taint nodes rpi5-7f7b2e m0net/infralab:PreferNoSchedule
# kubectl label nodes rpi5-7f7b2e m0net/infralab=true
# kubectl label nodes rpi5-7f7b2e m0net/run.jupyterhub=true

# kubectl label nodes rpi5-7f7cd7 m0net/run.jupyterlab=true

# kubectl label nodes rpi5-7f80fc m0net/run.jupyterlab=true
