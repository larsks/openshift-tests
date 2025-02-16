import pytest
from tests.helpers import assert_conditions


def test_all_nodes(kube, all_nodes, record_property):
    conditionMap = {
        "MemoryPressure": "False",
        "DiskPressure": "False",
        "PIDPressure": "False",
        "Ready": "True",
    }
    failed = 0
    for node in all_nodes:
        try:
            assert_conditions(node, conditionMap)
        except AssertionError as err:
            record_property(f"{node.metadata.name}", str(err))
            failed += 1

    if failed:
        pytest.fail("Some nodes were unhealthy.")
