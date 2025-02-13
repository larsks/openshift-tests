from tests.helpers import assert_conditions


def test_all_nodes(kube, record_property):
    conditionMap = {
        "MemoryPressure": "False",
        "DiskPressure": "False",
        "PIDPressure": "False",
        "Ready": "True",
    }
    nodes = kube.get("v1", "Node")
    record_property("node_count", len(nodes.items))
    for node in nodes.items:
        assert_conditions(node, conditionMap)
