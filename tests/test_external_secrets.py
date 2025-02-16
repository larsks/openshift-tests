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
def test_vault_access(kube, vault_check, testid, worker_nodes, record_property):
    """Test that all pods can reach the vault."""
    urls = discover_vault_urls(kube)
    if not urls:
        pytest.skip("This cluster does not use Vault for external secrets.")

    if not worker_nodes:
        pytest.skip("This cluster has no nodes.")

    for url in urls:
        with kube.manage(vault_check(url=url)):
            # wait for number of pods == number of nodes
            pods = kube.wait_for_n_objects(
                "v1",
                "Pod",
                len(worker_nodes),
                timeout=10,
                label_selector=f"app=openshift-tests,testid={testid},testname=test_vault_access",
            )

            okay, failed = kube.wait_for_jsonpath_all(
                pods.items, "status.containerStatuses[0].ready", True
            )

            if failed:
                for pod in failed:
                    record_property(
                        f"{pod.metadata.name} on {pod.spec.nodeName}", "failed"
                    )
                pytest.fail("Some pods were unable to connect to the vault.")


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
