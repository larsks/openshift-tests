import pytest

from tests.helpers import make_resource_fixture

pod_with_pvc = make_resource_fixture("pod_with_pvc")
pvc = make_resource_fixture("pvc")


def check_default_storage_class(kube):
    """Fail if no default storage class, since we required that for all the
    volume storage tests"""
    storage_classes = kube.get("storage.k8s.io/v1", "StorageClass")
    default_sc = next(
        (
            sc
            for sc in storage_classes.items
            if sc.metadata.annotations["storageclass.kubernetes.io/is-default-class"]
            == "true"
        ),
        0,
    )
    if not default_sc:
        pytest.fail("This cluster does not have a default storage class")

    return default_sc


def test_create_pvc(kube, pvc, record_property):
    """Test if we can create a PVC"""
    record_property(
        "default_storage_class", check_default_storage_class(kube).metadata.name
    )
    kube.wait_for_jsonpath(pvc[0], "status.phase", "Pending")
    _pvc = kube.refresh(pvc[0])
    scname = _pvc.spec.storageClassName
    sc = kube.get("storage.k8s.io/v1", "StorageClass", scname)
    bindmode = sc.volumeBindingMode

    if bindmode != "WaitForFirstConsumer":
        kube.wait_for_jsonpath(_pvc, "status.phase", "Bound")


def test_create_pod_with_pvc(kube, pod_with_pvc):
    """Test that we can create a PVC and bind it to a pod"""
    check_default_storage_class(kube)
    pod = pod_with_pvc[0]
    kube.wait_for_jsonpath(pod, "status.phase", "Running")

def test_create_pod_per_node_with_pvc(kube, pod_with_pvc):
    pass
