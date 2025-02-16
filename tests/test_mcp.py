import pytest

from tests.helpers import ResourceNotFoundError
from tests.helpers import assert_conditions


def test_mcp(kube):
    """Test that MachineConfigPools are healthy"""
    conditionMap = {
        "RenderDegraded": "False",
        "NodeDegraded": "False",
        "Degraded": "False",
        "Updated": "True",
        "Updating": "False",
    }
    try:
        pools = kube.get("machineconfiguration.openshift.io/v1", "MachineConfigPool")
    except ResourceNotFoundError:
        pytest.skip("This cluster does not have MachineConfigPools.")
    for pool in pools.items:
        assert_conditions(pool, conditionMap)

        assert pool.status.degradedMachineCount == 0
        assert pool.status.unavailableMachineCount == 0
        assert (
            pool.status.updatedMachineCount
            == pool.status.readyMachineCount
            == pool.status.machineCount
        )
