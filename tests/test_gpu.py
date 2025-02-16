import concurrent.futures
import pytest

from tests.helpers import make_template_fixture

gpu_workload = make_template_fixture("gpu_workload")

@pytest.mark.gpu
@pytest.mark.allnodes
def test_gpu_vectoradd(kube, gpu_workload, record_property):
    nodes = kube.get('v1', 'Node', label_selector="nvidia.com/gpu.present=true")
    if not nodes.items:
        pytest.skip('This cluster has no GPU nodes.')

    specs = []
    for node in nodes.items:
        specs.extend(list(gpu_workload(node=node.metadata.name)))

    with kube.manage(specs) as objects:
        okay, failed = kube.wait_for_jsonpath_all(objects, "status.phase", "Succeeded")

    if failed:
        for pod in failed:
            record_property(f"{pod.metadata.name} on {pod.spec.nodeName}", "failed")
        pytest.fail("Some pods were unable to run the GPU workload.")
