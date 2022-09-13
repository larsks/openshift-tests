# shellcheck disable=SC1083

# Verify that we can create a pod that offers a network service and access
# it from outside the cluster. Submit Pod, Service, and Route manifests,
# wait for the Service to get bound to an endpoint, and then attempt
# to access the service using the published Route.

setup() {
	load 'lib/bats-support/load'
	load 'lib/bats-assert/load'
	load 'lib/common.bash'

	${KUBECTL} -n "$TARGET_NAMESPACE" apply -k manifests/pod_with_service
}

teardown() {
	${KUBECTL} -n "$TARGET_NAMESPACE" delete -k manifests/pod_with_service
}


@test "pod starts up successfully" {
	wait_for_phase Running pod/test-pod
}

@test "service binds endpoint" {
	wait_for --for=jsonpath='{.subsets[0].ports[0].port}'=8080 endpoints/test-pod
}

@test "service accessible at route" {
	hostname=$(
		${KUBECTL} -n "$TARGET_NAMESPACE" \
		get route test-pod -o jsonpath='{.spec.host}'
	)
	timeout "${KUBE_LONG_TIMEOUT}" sh -c  '
		while ! curl -sf -o /dev/null $1; do
			sleep 1
		done
	' -- "$hostname"
}
