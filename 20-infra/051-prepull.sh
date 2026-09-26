#!/bin/sh

set -u

IMAGES="/etc/prepull/images.txt"
CRICTL="crictl --config /etc/prepull/crictl.yaml"
SA="/var/run/secrets/kubernetes.io/serviceaccount"
API="https://kubernetes.default.svc"

rand() {
	echo $(( $(od -An -N4 -tu4 /dev/urandom) % $1 ))
}

match() {
	[ "$1" = "*" ] && return 0
	curl -sfG --cacert "$SA/ca.crt" -H "Authorization: Bearer $(cat "$SA/token")" \
		--data-urlencode "fieldSelector=metadata.name=$NODE_NAME" \
		--data-urlencode "labelSelector=$1" \
		"$API/api/v1/nodes" | grep -q "\"name\": *\"$NODE_NAME\""
}

pull_all() {
	echo "$(date -Is) prepull start node=$NODE_NAME"
	ok=""
	ko=""
	grep -v '^[[:space:]]*\(#\|$\)' "$IMAGES" | while read -r selector image; do
		case " $ko " in *" $selector "*) continue ;; esac
		case " $ok " in
			*" $selector "*) ;;
			*)
				if match "$selector"; then
					ok="$ok $selector"
				else
					ko="$ko $selector"
					echo "skip $selector"
					continue
				fi
				;;
		esac
		echo "pull $image"
		$CRICTL pull "$image" || echo "fail $image"
	done

	$CRICTL images | awk '$2 == "<none>" {print $3}' | xargs -r $CRICTL rmi
	echo "$(date -Is) prepull done"
}

if [ "${1:-}" = "once" ]; then
	pull_all
	exit 0
fi

while true; do
	delay=$(( 6 * 24 * 3600 - 12 * 3600 + $(rand $((24 * 3600))) ))
	echo "$(date -Is) next in ${delay}s"
	sleep "$delay"
	pull_all
done

# eof
