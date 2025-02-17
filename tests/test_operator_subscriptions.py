import pytest
from tests.helpers import assert_conditions
from kubernetes.dynamic.exceptions import NotFoundError


def test_operator_subscriptions(kube, record_property):
    subs = kube.get(
        "operators.coreos.com/v1alpha1", "Subscription", all_namespaces=True
    )

    failed = 0
    for sub in subs.items:
        try:
            assert_conditions(sub, {"CatalogSourcesUnhealthy": "False"})
            assert [condition.type for condition in sub.status.conditions] == ['CatalogSourcesUnhealthy']
        except AssertionError as err:
            record_property(f"{sub.metadata.namespace}:{sub.metadata.name}", str(err))
            failed += 1

    if failed:
        pytest.fail("Some subscriptions were unhealthy.")
