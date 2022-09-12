# Verify that we can create a PersistentVolumeClaim. Submit a PVC manifest
# and wait for it to become `Bound`.

setup() {
	load 'lib/bats-support/load'
	load 'lib/bats-assert/load'
	load 'lib/common.bash'
}

teardown() {
	${KUBECTL} -n "$TARGET_NAMESPACE" delete -f manifests/pvc.yaml
}


@test "can create pvc" {
	${KUBECTL} -n "$TARGET_NAMESPACE" apply -f manifests/pvc.yaml
	wait_for_phase Bound pvc/test-volume
}
