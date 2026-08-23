# lab0-k8s

- git update-ref -d HEAD && git commit -a -m Initial\ commit && git push -f
- git commit -a -m commit-$(date +'%Y-%m-%d-%H-%M-%S') && git push
- git gc --prune=now
- git fsck

- kubectl kustomize overlay/nuc4x | md5sum
- kubectl kustomize overlay/clval | md5sum
- kubectl kustomize overlay/cabhs | md5sum
- kubectl kustomize overlay/fenix | md5sum
- kubectl kustomize overlay/radio | md5sum
- kubectl kustomize overlay/reloj | md5sum
- kubectl kustomize overlay/rpi5  | md5sum

- kubectl kustomize overlay/nuc4x | ssh nuc4x.srv.menoscero.com kubectl apply -f -
- kubectl kustomize overlay/clval | ssh clval.vps.menoscero.com kubectl apply -f -
- kubectl kustomize overlay/cabhs | ssh cabhs.srv.menoscero.com kubectl apply -f -
- kubectl kustomize overlay/fenix | ssh fenix.ubb.menoscero.com kubectl apply -f -
- kubectl kustomize overlay/radio | ssh radio.ubb.menoscero.com kubectl apply -f -
- kubectl kustomize overlay/reloj | ssh reloj.ubb.menoscero.com kubectl apply -f -
- kubectl kustomize overlay/rpi5  | ssh 100.64.128.131 kubectl apply -f -
