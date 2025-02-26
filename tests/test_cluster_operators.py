import pytest

from tests.helpers import assert_conditions
from tests.helpers import ResourceNotFoundError


def test_cluster_operators(kube, record_property):
    """Test that all cluster operators are healthy"""
    conditionMap = {
        "Degraded": "False",
        "Progressing": "False",
        "Available": "True",
        "Upgradeable": "True",
    }
    try:
        ops = kube.get("config.openshift.io/v1", "ClusterOperator")
    except ResourceNotFoundError:
        pytest.skip("This cluster does not have cluster operators.")

    failed = 0
    for op in ops.items:
        try:
            assert_conditions(op, conditionMap)
        except AssertionError as err:
            record_property(f"{op.metadata.name}", str(err))
            failed += 1

    if failed:
        pytest.fail("Some cluster operators are unhealthy")
