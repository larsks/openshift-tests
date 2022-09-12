# Verify that a pod can successfully access a service provided by another
# Pod. This tests cluster DNS and network connectivity between Pods.

setup() {
	load 'lib/bats-support/load'
	load 'lib/bats-assert/load'
	load 'lib/common.bash'
}

teardown() {
	${KUBECTL} -n "$TARGET_NAMESPACE" delete -k manifests/two_pods_talking
}


@test "pod communication is successful" {
	${KUBECTL} -n "$TARGET_NAMESPACE" apply -k manifests/two_pods_talking

	wait_for_phase Running pod/test-pod1
	wait_for_phase Running pod/test-pod2
}
