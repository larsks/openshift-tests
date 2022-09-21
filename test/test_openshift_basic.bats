# Test basic OpenShift functionality: Can we perform simple API operations like
# listing namespaces? Is the ClusterVersion resource healthy?

setup() {
	load 'lib/bats-support/load'
	load 'lib/bats-assert/load'
	load 'lib/common.bash'
}

@test "can get default namespace" {
	${KUBECTL} get ns default
}

@test "clusterversion is available" {
	${KUBECTL} get clusterversion/version \
		-o jsonpath='{.status.conditions[?(@.type=="Available")].status}' |
	grep -q True
	${KUBECTL} get clusterversion/version \
		-o jsonpath='{.status.conditions[?(@.type=="Failing")].status}' |
	grep -q False
}
