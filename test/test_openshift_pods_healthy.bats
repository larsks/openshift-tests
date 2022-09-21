# Test that there are no failing or pending pods in openshift-* namespaces.

setup() {
	load 'lib/bats-support/load'
	load 'lib/bats-assert/load'
	load 'lib/common.bash'
}

@test "no openshift pods are failing" {
	diff -u /dev/null \
		<(
			${KUBECTL} get --no-headers pod -A  |
			awk '$1 ~ /^openshift/ {print}' |
			grep -Ev "Running|Completed"
		)
}
