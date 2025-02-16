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

    with kube.manage(specs) as objects, concurrent.futures.ThreadPoolExecutor() as pool:
        tasks = []
        failed = 0
        for obj in objects:
            tasks.append(
                pool.submit(
                    kube.wait_for_jsonpath,
                    obj,
                    "status.phase",
                    "Succeeded",
                    timeout=120,
                )
            )

        for task in concurrent.futures.as_completed(tasks):
            # If kube.wait_for_jsonpath raised an exception, it
            # will be visible here.
            try:
                task.result()
            except TimeoutError as err:
                msg, pod = err.args
                record_property(pod.metadata.name, "failed")
                failed += 1

    if failed > 0:
        pytest.fail("Some pods failed to run the GPU workload.")
