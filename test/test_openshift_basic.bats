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
			awk '$1 ~ /^openshift/ {print}' |
			grep -Ev "Running|Completed"
		)
}

@test "clusterversion is available" {
	${KUBECTL} get clusterversion/version \
		-o jsonpath='{.status.conditions[?(@.type=="Available")].status}' |
	grep -q True
	${KUBECTL} get clusterversion/version \
		-o jsonpath='{.status.conditions[?(@.type=="Failing")].status}' |
	grep -q False
}
