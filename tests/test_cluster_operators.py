from tests.helpers import assert_conditions


def test_cluster_operators(kube):
    """Test that all cluster operators are healthy"""
    conditionMap = {
        "Degraded": "False",
        "Progressing": "False",
        "Available": "True",
        "Upgradeable": "True",
    }
    ops = kube.get("config.openshift.io/v1", "ClusterOperator")
    for op in ops.items:
        assert_conditions(op, conditionMap)
