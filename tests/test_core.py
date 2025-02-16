from tests.helpers import make_resource_fixture

pod = make_resource_fixture("pod")
pod_with_service = make_resource_fixture("pod_with_service")
two_pods_talking = make_resource_fixture("two_pods_talking")
job_check_url = make_resource_fixture("job_check_url", url="https://www.google.com")


def test_create_pod(kube, pod):
    """Test that we can successfully create a pod."""
    kube.wait_for_jsonpath(pod[0], "status.phase", "Running")


def test_create_pod_with_service(kube, pod_with_service):
    """Test that we can create a pod and an associated service, and that the
    service successfully binds to the pod."""
    pod = pod_with_service[0]
    kube.wait_for_jsonpath(pod, "status.phase", "Running")

    endpoints = kube.get("v1", "Endpoints", pod.metadata.name)
    kube.wait_for_jsonpath(endpoints, "subsets[0].ports[0].port", 8080)


def test_pod_external_connectivity(kube, job_check_url, testid):
    """Test that a pod can reach an outside endpoint."""
    try:
        job = job_check_url[0]
        kube.wait_for_jsonpath(job, "status.succeeded", 1)
    finally:
        kube.delete_gkv('v1', 'Pod', label_selector=f'testid={testid},testname=test_pod_external_connectivity')


def test_two_pods_talking(kube, two_pods_talking):
    """Test that a pod can successfully access a service running in another pod."""
    for obj in two_pods_talking:
        if obj.kind == "Pod":
            kube.wait_for_jsonpath(obj, "status.phase", "Running")

    for obj in two_pods_talking:
        if obj.kind == "Pod":
            kube.wait_for_jsonpath(obj, "status.containerStatuses[0].ready", True)
