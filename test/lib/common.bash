#!/bin/bash
# shellcheck disable=SC1083

: "${KUBECTL:=kubectl}"
: "${TARGET_NAMESPACE:=default}"
: "${KUBE_LONG_TIMEOUT:=30}"

export TARGET_NAMESPACE KUBECTL KUBE_LONG_TIMEOUT

wait_for_phase() {
	local phase=$1
	local object=$2

	wait_for --for=jsonpath={.status.phase}="$phase" "$object"
}

wait_for() {
	timeout "${KUBE_LONG_TIMEOUT}" sh -c '
		while ! ${KUBECTL} -n "$TARGET_NAMESPACE" wait "$@"; do
			sleep 1
		done
	' -- "$@"
}

cluster_has_apigroup() {
	${KUBECTL} api-resources --api-group "$1" --no-headers |
		grep -q .
}
