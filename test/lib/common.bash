: "${KUBECTL:=kubectl}"
: "${TARGET_NAMESPACE:=default}"
: "${KUBE_LONG_TIMEOUT:=30}"

export TARGET_NAMESPACE KUBECTL KUBE_LONG_TIMEOUT

wait_for_phase() {
	${KUBECTL} -n "$TARGET_NAMESPACE" wait \
		--for=jsonpath='{.status.phase}'="$1" \
		--timeout="${KUBECTL_LONG_TIMEOUT}s" "$2"
}

cluster_has_apigroup() {
	${KUBECTL} api-resources --api-group "$1" --no-headers |
		grep -q .
}
