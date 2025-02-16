import concurrent.futures

import pytest

from tests.helpers import ResourceNotFoundError
from tests.helpers import assert_conditions
from tests.helpers import make_template_fixture
from tests.helpers import get_condition
from tests.helpers import get_conditions

vault_check = make_template_fixture("vault_check")


def discover_vault_urls(kube):
    """Get a set of vault URLs used in SecretStores and ClusterSecretStores"""
    try:
        stores = kube.get(
            "external-secrets.io/v1beta1", "SecretStore", all_namespaces=True
        )
        cluster_stores = kube.get("external-secrets.io/v1beta1", "ClusterSecretStore")
    except ResourceNotFoundError:
        pytest.skip("This cluster does not have external secrets.")

    urls = set(
        obj.spec.provider.vault.server
        for obj in stores.items + cluster_stores.items
        if obj.spec.provider.vault
    )

    return urls


@pytest.mark.allnodes
def test_vault_access(kube, vault_check, testid, record_property):
    """Test that all pods can reach the vault."""
    urls = discover_vault_urls(kube)
    if not urls:
        pytest.skip("This cluster does not use Vault for external secrets.")

    nodes = kube.get_worker_nodes()
    if not nodes:
        pytest.skip("This cluster has no nodes.")

    for url in urls:
        with kube.manage(vault_check(url=url)):
            # wait for number of pods == number of nodes
            try:
                pods = kube.wait_for_n_objects(
                    "v1",
                    "Pod",
                    len(nodes),
                    timeout=10,
                    label_selector=f"app=openshift-tests,testid={testid},testname=test_vault_access",
                )
            except TimeoutError as err:
                pytest.fail(str(err))

            # wait for pods to become ready
            failed = 0
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

                for task in concurrent.futures.as_completed(tasks):
                    # If kube.wait_for_jsonpath raised an exception, it
                    # will be visible here.
                    try:
                        pod = task.result()
                    except TimeoutError as err:
                        msg, pod = err.args
                        record_property(pod.spec.nodeName, "failed")
                        failed += 1

            if failed:
                pytest.fail("Some pods were unable to reach the vault.")


def test_secretstores(kube, record_property):
    """Test that SecretStores are healthy"""
    try:
        stores = kube.get(
            "external-secrets.io/v1beta1", "SecretStore", all_namespaces=True
        )
    except ResourceNotFoundError:
        pytest.skip("This cluster does not have external secrets.")
    if not stores.items:
        pytest.skip("There are no SecretStore resources")
    for store in stores.items:
        ready = get_condition(store, "Ready")
        if ready.status != "True":
            record_property(
                f"{store.metadata.name}",
                f"{ready.reason}: {ready.message}",
            )
        assert_conditions(store, {"Ready": "True"})


def test_clustersecretstores(kube, record_property):
    """Test that ClusterSecretStores are healthy"""
    try:
        stores = kube.get("external-secrets.io/v1beta1", "ClusterSecretStore")
    except ResourceNotFoundError:
        pytest.skip("This cluster does not have external secrets.")
    if not stores.items:
        pytest.skip("There are no ClusterSecretStore resources")
    for store in stores.items:
        ready = get_condition(store, "Ready")
        if ready.status != "True":
            record_property(
                f"{store.metadata.name}",
                f"{ready.reason}: {ready.message}",
            )
        assert_conditions(store, {"Ready": "True"})
