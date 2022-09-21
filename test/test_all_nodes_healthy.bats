# Verify that all nodes are healthy.

setup() {
	load 'lib/bats-support/load'
	load 'lib/bats-assert/load'
	load 'lib/common.bash'
}

@test "all nodes are healthy" {
	${KUBECTL} get nodes --no-headers -o custom-columns=":metadata.name" |
	while read -r node; do
		${KUBECTL} get node "$node" \
			-o jsonpath='{.status.conditions[?(@.type=="Ready")].status}' |
			grep -q True
	done
}
