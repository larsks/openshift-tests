from tests.helpers import assert_conditions


def test_clusterversion(kube):
    """Test that the ClusterVersion resource is healthy"""
    conditionMap = {
        "RetrievedUpdates": "True",
        "ImplicitlyEnabledCapabilities": "False",
        "PayloadLoaded": "True",
        "Available": "True",
        "Failing": "False",
        "Progressing": "False",
        "Upgradeable": "True",
    }
    cv = kube.get("config.openshift.io/v1", "ClusterVersion", "version")

    assert_conditions(cv, conditionMap)
