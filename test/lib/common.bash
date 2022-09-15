: "${KUBECTL:=kubectl}"
: "${TARGET_NAMESPACE:=default}"

export TARGET_NAMESPACE KUBECTL

wait_for_phase() {
	${KUBECTL} -n "$TARGET_NAMESPACE" wait \
		--for=jsonpath='{.status.phase}'="$1" \
		--timeout=30s "$2"
}

cluster_has_apigroup() {
	${KUBECTL} api-resources --api-group "$1" --no-headers |
		grep -q .
}
