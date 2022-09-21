# Verify that we can write and sync data to a PVC. Create PVC and Job
# manifests and wait for the Job to complete.

setup() {
	load 'lib/bats-support/load'
	load 'lib/bats-assert/load'
	load 'lib/common.bash'
}

teardown() {
	${KUBECTL} -n "$TARGET_NAMESPACE" delete -k manifests/test_write_pvc
}

@test "can write to pvc" {
	${KUBECTL} -n "$TARGET_NAMESPACE" apply -k manifests/test_write_pvc
	wait_for --for=condition=Complete job/test-job
}
