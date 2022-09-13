# Verify that we can successfully create a Secret from an ExternalSecret
# resource.

setup() {
	load 'lib/bats-support/load'
	load 'lib/bats-assert/load'
	load 'lib/common.bash'

	cluster_has_apigroup external-secrets.io ||
		skip "cluster does not support external secrets"
}

teardown() {
	# Teardown will be called even if we decide we should skip these tests in setup(),
	# which means we need to avoid trying to delete the external secret if the
	# cluster doesn't have external secrets installed.
	if cluster_has_apigroup external-secrets.io; then
		${KUBECTL} -n "$TARGET_NAMESPACE" delete \
			--ignore-not-found -f manifests/externalsecret.yaml
	fi
}

external_secret_common() {
	wait_for --for=condition=Ready externalsecret/test-secret
	timeout "${KUBE_LONG_TIMEOUT}" sh -c '
		while ! ${KUBECTL} -n "$TARGET_NAMESPACE" get secret test-secret; do
			sleep 1
		done
	'
}

@test "can create an externalsecret using clustersecretstore" {
	[[ -n "$CLUSTER_SECRET_STORE_NAME" ]] || skip "CLUSTER_SECRET_STORE_NAME named is not defined"
	[[ -n "$SECRET_PATH" ]] || skip "SECRET_PATH is not defined"

	${KUBECTL} -n "$TARGET_NAMESPACE" get clustersecretstore "$CLUSTER_SECRET_STORE_NAME" ||
		skip "clustersecretstore $CLUSTER_SECRET_STORE_NAME does not exist"

	sed \
		-e "s|SECRET_STORE_NAME|$CLUSTER_SECRET_STORE_NAME|g" \
		-e "s|SECRET_STORE_TYPE|ClusterSecretStore|g" \
		-e "s|SECRET_PATH|$SECRET_PATH|g" \
		manifests/externalsecret.yaml |
			${KUBECTL} -n "$TARGET_NAMESPACE" apply -f-

	external_secret_common
}

@test "can create an externalsecret using secretstore" {
	[[ -n "$SECRET_STORE_NAME" ]] || skip "SECRET_STORE_NAME named is not defined"
	[[ -n "$SECRET_PATH" ]] || skip "SECRET_PATH is not defined"

	${KUBECTL} -n "$TARGET_NAMESPACE" get secretstore "$SECRET_STORE_NAME" ||
		skip "secretstore $SECRET_STORE_NAME does not exist in $TARGET_NAMESPACE"

	sed \
		-e "s|SECRET_STORE_NAME|$SECRET_STORE_NAME|g" \
		-e "s|SECRET_STORE_TYPE|SecretStore|g" \
		-e "s|SECRET_PATH|$SECRET_PATH|g" \
		manifests/externalsecret.yaml |
			${KUBECTL} -n "$TARGET_NAMESPACE" apply -f-

	external_secret_common
}
