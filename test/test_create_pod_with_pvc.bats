# Verify that a Pod can successfully mount a PersistentVolumeClaim. Submit
# PVC and Pod manifests and wait for the Pod to reach phase `Running`.

setup() {
	load 'lib/bats-support/load'
	load 'lib/bats-assert/load'
	load 'lib/common.bash'
}

teardown() {
	${KUBECTL} -n "$TARGET_NAMESPACE" delete -k manifests/pod_with_pvc
}

@test "can create pod with pvc" {
	${KUBECTL} -n "$TARGET_NAMESPACE" apply -k manifests/pod_with_pvc
	wait_for_phase Running pod/test-pod
}
