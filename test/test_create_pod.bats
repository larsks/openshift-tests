# Verify that we can create a Pod: Submit a Pod manifest and wait for it to
# enter phase `Running`.

setup() {
	load 'lib/bats-support/load'
	load 'lib/bats-assert/load'
	load 'lib/common.bash'
}

teardown() {
	${KUBECTL} -n "$TARGET_NAMESPACE" delete -f manifests/pod.yaml
}


@test "can create pod" {
	${KUBECTL} -n "$TARGET_NAMESPACE" apply -f manifests/pod.yaml
	wait_for_phase Running pod/test-pod
}
