import pytest
from tests.helpers import assert_conditions
from tests.helpers import ResourceNotFoundError


def test_cluster_operators(kube):
    """Test that all cluster operators are healthy"""
    conditionMap = {
        "Degraded": "False",
        "Progressing": "False",
        "Available": "True",
        "Upgradeable": "True",
    }
    try:
        ops = kube.get("config.openshift.io/v1", "ClusterOperator")
    except  ResourceNotFoundError:
        pytest.skip("This cluster does not have cluster operators.")
    for op in ops.items:
        assert_conditions(op, conditionMap)
