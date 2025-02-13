from tests.helpers import assert_conditions


def test_clusterversion(kube, record_property):
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

    record_property("channel", cv.spec.channel)
    record_property("version", cv.status.history[0].version)

    assert_conditions(cv, conditionMap)
