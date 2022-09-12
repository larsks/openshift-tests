# Verify that we can successfully create an ObjectBucketClaim: submit an
# OBC manifest and wait for it to become `Bound`.

setup() {
	load 'lib/bats-support/load'
	load 'lib/bats-assert/load'
	load 'lib/common.bash'
}

teardown() {
	${KUBECTL} -n "$TARGET_NAMESPACE" delete -f manifests/obc.yaml
}


@test "can create obc" {
	${KUBECTL} -n "$TARGET_NAMESPACE" apply -f manifests/obc.yaml
	wait_for_phase Bound obc/test-bucket
}
