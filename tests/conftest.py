import datetime
import random
import string
import subprocess
import tempfile
from pathlib import Path

import jinja2
import kubernetes.config
import pytest
from pytest import fixture

from tests.helpers import KubeHelper


@fixture
def testimage(request):
    """Return the name of the test image to use in tests"""
    return request.config.getoption("--test-image")


@fixture(scope="function")
def testid() -> str:
    """Returns a random 6-character string that can be used when generating resource names"""
    prefix = "".join(random.sample(string.ascii_lowercase, 6))
    now = datetime.datetime.now().isoformat("-", timespec="seconds").replace(":", "-")
    return f"{prefix}-{now}"


@fixture
def kubeconfig():
    """Ensure that the kubernetes config has been loaded"""
    kubernetes.config.load_kube_config()


@fixture
def namespace(request, kubeconfig) -> str:
    """Return the namespace in which to create namespaced resources"""
    if namespace := request.config.getoption("--namespace"):
        return namespace

    try:
        return kubernetes.config.list_kube_config_contexts()[1]["context"]["namespace"]
    except (KeyError, IndexError):
        return "default"


@fixture
def manifests():
    """Return a jinja2 Environment for accessing manifest templates"""
    env = jinja2.Environment(loader=jinja2.FileSystemLoader("manifests"))
    return env


@fixture
def tmpdir(testid):
    """Return the path to a temporary directory. The directory will be removed when the test run is complete."""
    with tempfile.TemporaryDirectory(prefix=f"test-{testid}") as dir:
        yield Path(dir)


@fixture
def kube(testid, namespace, kubeconfig):
    """Return a KubeHelper object for interacting with the Kubernetes api"""
    return KubeHelper(testid, namespace=namespace)


@fixture
def all_nodes(kube):
    return kube.get("v1", "Node").items


@fixture
def worker_nodes(kube):
    return kube.get_worker_nodes()


def pytest_addoption(parser):
    """Add custom command line options"""
    parser.addoption(
        "--test-image",
        action="store",
        help="Container image to use in tests",
        default="ghcr.io/larsks/openshift-tests:feature-python",
    )
    parser.addoption(
        "--namespace", action="store", help="Namespace in which to create resources"
    )
    parser.addoption(
        "--cluster-admin",
        action="store_true",
        default=False,
        help="Enable tests that require cluster admin privileges",
    )


def pytest_configure(config):
    """Register custom markers"""
    config.addinivalue_line(
        "markers", "cluster_admin: tests that require cluster admin privileges"
    )
    config.addinivalue_line("markers", "allnodes: tests that spawn pods on all nodes")
    config.addinivalue_line("markers", "gpu: tests that require gpu hardware")


def pytest_collection_modifyitems(config, items):
    # Arrange to only run tests marked with the cluster_admin marker when you provide the --cluster-admin flag
    # on the command line. See tests/test_cluster_admin_example.py for an example.
    if config.getoption("--cluster-admin"):
        return
    skip_cluster_admin = pytest.mark.skip(
        reason="This test requires cluster admin privileges."
    )
    for item in items:
        if "cluster_admin" in item.keywords:
            item.add_marker(skip_cluster_admin)
