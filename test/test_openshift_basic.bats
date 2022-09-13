# Test basic OpenShift functionality: Can we perform simple API operations
# like listing namespaces? Are there any failed pods? Is the ClusterVersion
# resource `Available`? Etc.

setup() {
	load 'lib/bats-support/load'
	load 'lib/bats-assert/load'
	load 'lib/common.bash'
}

@test "can get default namespace" {
	${KUBECTL} get ns default
}

@test "no openshift pods are failing" {
	diff -u /dev/null \
		<(
			${KUBECTL} get --no-headers pod -A  |
			grep openshift- |
			grep -Ev "Running|Completed"
		)
}

@test "clusterversion is available" {
	wait_for --for=condition=Available clusterversion/version
}
