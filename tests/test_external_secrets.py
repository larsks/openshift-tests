import concurrent.futures
import time

import pytest

from tests.helpers import assert_conditions, make_template_fixture

vault_check = make_template_fixture(
    "vault_check", url="https://vault-ui-vault.apps.nerc-ocp-infra.rc.fas.harvard.edu"
)


def test_vault_access(kube, vault_check, testid):
    """Test that all pods can reach the vault."""
    nodes = kube.get("v1", "Node", label_selector="node-role.kubernetes.io/worker")

    # Wait for the daemonset to create the pods
    t_start = time.time()
    while True:
        pods = kube.get("v1", "Pod", label_selector=f"app=vault-check,testid={testid}")
        if len(pods.items) == len(nodes.items):
            break

        if time.time() - t_start > 30:
            raise TimeoutError("failed to reach expected number of pods")

    # Wait for pods to become ready
    with concurrent.futures.ThreadPoolExecutor() as pool:
        tasks = []
        for pod in pods.items:
            tasks.append(
                pool.submit(
                    kube.wait_for_jsonpath,
                    pod,
                    "status.containerStatuses[0].ready",
                    True,
                )
            )

        try:
            for task in concurrent.futures.as_completed(tasks):
                # If kube.wait_for_jsonpath raised an exception, it
                # will be visible here.
                task.result()
        except TimeoutError:
            pytest.fail("Some pods were unable to reach the vault.")


def test_secretstores(kube):
    """Test that SecretStores are healthy"""
    stores = kube.get("external-secrets.io/v1beta1", "SecretStore", all_namespaces=True)
    if not stores.items:
        pytest.skip("There are no SecretStore resources")
    for store in stores.items:
        assert_conditions(store, {"Ready": "True"})


def test_clustersecretstores(kube):
    """Test that ClusterSecretStores are healthy"""
    stores = kube.get(
        "external-secrets.io/v1beta1", "ClusterSecretStore", all_namespaces=True
    )
    if not stores.items:
        pytest.skip("There are no ClusterSecretStore resources")
    for store in stores.items:
        assert_conditions(store, {"Ready": "True"})
