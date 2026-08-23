#!/bin/sh

set -eux

TALOSCP="${TALOSCP:-192.168.64.100}"
TLSDSK="${TLSDSK:-/dev/vda}"

log() {
    printf '\n==> %s\n' "$*"
}

error() {
    printf 'Error: %s\n' "$*" >&2
    exit 1
}

usage() {
    cat <<EOF
Usage:
  $0 init
  $0 inspect <node-ip>
  $0 controlplane <node-patch> <node-ip>
  $0 bootstrap
  $0 worker <node-patch> <node-ip>
  $0 upgrade [node-ip]
  $0 upk8s

Examples:
  $0 init
  $0 inspect 192.168.64.10
  $0 controlplane 906-node-cp-101.yaml 192.168.64.10
  $0 bootstrap
  $0 worker       906-node-w-102.yaml  192.168.64.11
  $0 upgrade
  $0 upgrade 192.168.64.10
EOF
}

require_file() {
    [ -f "$1" ] || error "File not found: $1"
}

main() {
    COMMAND="${1:-}"
    case "$COMMAND" in
        init)
            if [ -f 901-secrets.yaml ]; then
                log "Keeping existing secrets file: 901-secrets.yaml"
            else
                log "Creating secrets file: 901-secrets.yaml"
                talosctl gen secrets --output-file 901-secrets.yaml
            fi
            log "Recreating Talos client configuration: 901-talosconfig"
            rm -f 901-talosconfig
            talosctl gen config \
                cluster.local \
                "https://${TALOSCP}:6443" \
                --with-secrets 901-secrets.yaml \
                --output-types talosconfig \
                --output 901-talosconfig
            ;;

        inspect)
            [ "$#" -le 2 ] || error "Usage: $0 inspect [node-ip]"
            if [ "$#" -eq 2 ]; then
                TALOSIP="$2"
                log "Inspecting Talos node: $TALOSIP"
                talosctl get links --insecure --nodes "$TALOSIP"
                talosctl get disks --insecure --nodes "$TALOSIP"
                talosctl get discoveredvolumes --insecure --nodes "$TALOSIP"
                talosctl get volumestatus --insecure --nodes "$TALOSIP"
                talosctl get mountstatus --insecure --nodes "$TALOSIP"
                talosctl get pcidevices --insecure --nodes "$TALOSIP"
            else
                log "Inspecting Talos using the configured node"
                talosctl get links
                talosctl get disks
                talosctl get discoveredvolumes
                talosctl get volumestatus
                talosctl get mountstatus
                talosctl get pcidevices
            fi
            ;;

        controlplane | cp)
            [ "$#" -eq 3 ] ||
                error "Usage: $0 controlplane <node-patch> <node-ip>"
            PATCH="$2"
            TALOSIP="$3"
            require_file 901-secrets.yaml
            require_file 902-disk.yaml
            require_file 902-security.yaml
            require_file "$PATCH"
            OUTFILE="905-node-cp-${TALOSIP}.yaml"
            log "Generating control-plane configuration: $OUTFILE"
            rm -f "$OUTFILE"
            talosctl gen config \
                cluster.local \
                "https://${TALOSCP}:6443" \
                --install-disk "$TLSDSK" \
                --with-docs=false \
                --with-secrets 901-secrets.yaml \
                --config-patch @902-disk.yaml \
                --config-patch-control-plane @902-security.yaml \
                --config-patch-control-plane "@${PATCH}" \
                --output-types controlplane \
                --output "$OUTFILE"
            log "Applying $OUTFILE to $TALOSIP"
            talosctl apply-config \
                --insecure \
                --nodes "$TALOSIP" \
                --file "$OUTFILE"
            ;;

        worker | w)
            [ "$#" -eq 3 ] ||
                error "Usage: $0 worker <node-patch> <node-ip>"
            PATCH="$2"
            TALOSIP="$3"
            require_file 901-secrets.yaml
            require_file 902-disk.yaml
            require_file "$PATCH"
            OUTFILE="905-node-w-${TALOSIP}.yaml"
            log "Generating worker configuration: $OUTFILE"
            rm -f "$OUTFILE"
            talosctl gen config \
                cluster.local \
                "https://${TALOSCP}:6443" \
                --install-disk "$TLSDSK" \
                --with-docs=false \
                --with-secrets 901-secrets.yaml \
                --config-patch @902-disk.yaml \
                --config-patch-worker "@${PATCH}" \
                --output-types worker \
                --output "$OUTFILE"
            log "Applying $OUTFILE to $TALOSIP"
            talosctl apply-config \
                --insecure \
                --nodes "$TALOSIP" \
                --file "$OUTFILE"
            ;;

        bootstrap)
            [ "$#" -eq 1 ] || error "Usage: $0 bootstrap"
            require_file 901-talosconfig
            log "Configuring talosctl for control plane: $TALOSCP"
            mkdir -p "$HOME/.talos"
            rm -f "$HOME/.talos/config"
            talosctl config merge 901-talosconfig
            talosctl config endpoints "$TALOSCP"
            talosctl config node "$TALOSCP"
            talosctl config contexts
            log "Bootstrapping the Talos cluster"
            talosctl bootstrap
            log "Retrieving Kubernetes configuration"
            mkdir -p "$HOME/.kube"
            rm -f "$HOME/.kube/config"
            talosctl kubeconfig
            ;;

        upgrade)
            [ "$#" -le 2 ] || error "Usage: $0 upgrade [node-ip]"
            if [ "$#" -eq 2 ]; then
                TALOSIP="$2"
                log "Upgrading Talos node: $TALOSIP"
                talosctl upgrade --nodes "$TALOSIP"
            else
                log "Upgrading Talos using the configured node"
                talosctl upgrade
            fi
            ;;

        upk8s)
            [ "$#" -eq 1 ] || error "Usage: $0 upk8s"
            log "Upgrading Kubernetes"
            talosctl upgrade-k8s --pre-pull-images
            ;;

        help | -h | --help | "")
            usage
            ;;

        *)
            usage
            error "Unknown command: $COMMAND"
            ;;
    esac
}

main "$@"
