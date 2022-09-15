#!/bin/bash

FORCE=0
KUBECTL=${KUBECTL:-kubectl}

usage() {
	echo "${0##*/}: usage: ${0##*/} [--force] [...bats options...]"
}

while :; do
	case "$1" in
		--force|-f)
			FORCE=1
			shift
			;;

		--help|-h)
			usage
			exit 0
			;;

		--)	shift
			break
			;;

		-*)	echo "ERROR: invalid option: $1" >&2
			usage >&2
			exit 2
			;;

		*)	break
			;;
	esac
done

if ! [ -x test/lib/bats/bin/bats ]; then
	cat <<-EOF >&2

	It looks like 'bats' is missing! You may need to initialize
	submodules in this repository. Try running:

	    git submodule update --init

	EOF

	exit 1
fi

if ! (( FORCE )) && ! ${KUBECTL} get nodes > /dev/null 2>&1; then
	cat <<-EOF >&2

	${KUBECTL} was unable to successfully run the "get nodes" command.
	This suggests that either you are not authenticated to a Kubernetes
	cluster or that you do not have appropriate privileges.

	You must be authenticated to an OpenShift or Kubernetes cluster with
	cluster-admin privileges in order for these tests to run.

	If you would like to run the tests anyway, re-run this script with the
	"--force" option.

	EOF

	exit 1
fi

./test/lib/bats/bin/bats "${@:-test}"
