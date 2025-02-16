import time
from contextlib import contextmanager

import jsonpath_ng as jsonpath
import pytest
import yaml
from kubernetes import client, dynamic
from kubernetes.dynamic.exceptions import ResourceNotFoundError  # noqa


class KubeHelper:
    """This is a help class that makes interacting with the kubernetes dynamic api somewhat easier"""

    def __init__(self, testid, namespace="default"):
        self.testid = testid
        self.namespace = namespace
        self.apiclient = client.ApiClient()
        self.dynclient = dynamic.DynamicClient(self.apiclient)

    @contextmanager
    def manage(self, specs):
        """Create objects from specs, return the objects, then delete them when the context closes."""
        objects = self.create_objects(specs)
        try:
            yield objects
        finally:
            self.delete_objects(objects)

    def resource_for_obj(self, obj):
        """Return a `Resource` for the given object. This is used by the dynamic client
        to interact with objects of the specified type."""
        return self.dynclient.resources.get(
            api_version=obj["apiVersion"], kind=obj["kind"]
        )

    def resource_for(self, api_version, kind):
        """Return a `Resource` for the given api_version and kind."""
        return self.dynclient.resources.get(api_version=api_version, kind=kind)

    def get(
        self,
        api_version,
        kind,
        name=None,
        namespace=None,
        all_namespaces=False,
        **kwargs,
    ):
        """Get an object or list of objects by specifying the api_version and kind."""
        if all_namespaces:
            namespace = None
        elif namespace is None:
            namespace = self.namespace
        rsrc = self.dynclient.resources.get(api_version=api_version, kind=kind)
        return self.dynclient.get(rsrc, name=name, namespace=namespace, **kwargs)

    def refresh(self, obj):
        """Fetch updated information for the given object."""
        rsrc = self.resource_for_obj(obj)
        return self.dynclient.get(
            rsrc, name=obj.metadata.name, namespace=obj.metadata.namespace
        )

    def create(self, spec):
        """Create the resource described in `spec` and return the resulting object."""
        rsrc = self.resource_for_obj(spec)
        return self.dynclient.create(rsrc, body=spec, namespace=self.namespace)

    def delete_gkv(self, api_version, kind, namespace=None, **kwargs):
        if namespace is None:
            namespace = self.namespace
        rsrc = self.dynclient.resources.get(api_version=api_version, kind=kind)
        return self.dynclient.delete(rsrc, namespace=namespace, **kwargs)

    def delete(self, obj):
        """Delete the given object."""
        rsrc = self.resource_for_obj(obj)
        return self.dynclient.delete(
            rsrc, name=obj.metadata.name, namespace=obj.metadata.namespace
        )

    def create_objects(self, specs):
        """Create all the objects described in `specs`. Return a list of the created objects."""
        objects = []
        for spec in specs:
            spec["metadata"].setdefault("labels", {})["testid"] = self.testid
            objects.append(self.create(spec))

        return objects

    def delete_objects(self, objects):
        """Delete all the given objects."""
        for obj in objects:
            self.delete(obj)

    def wait_for_jsonpath(self, obj, expr_raw, value, timeout=30):
        """Poll a jsonpath expression until it has the expected value or until we exceed the timeout."""
        t_start = time.time()
        expr = jsonpath.parse(expr_raw)
        while True:
            obj = self.refresh(obj)
            res = expr.find(obj)
            assert len(res) <= 1

            if res and res[0].value == value:
                break

            if time.time() - t_start > timeout:
                raise TimeoutError(
                    f'expression {expr} for {obj.kind} "{obj.metadata.name}" failed to reach value {value}',
                    obj,
                )

            time.sleep(1)

        return obj

    def wait_for_n_objects(self, api_version, kind, count, timeout=30, **kwargs):
        """Poll until there are count kind objects, or until we exceed the timeout"""
        t_start = time.time()
        while True:
            objs = self.get(api_version, kind, **kwargs)
            if len(objs.items) == count:
                return objs

            if time.time() - t_start > timeout:
                raise TimeoutError(
                    f"expected {count} objects of type {kind}, but found {len(objs.items)}"
                )

    def get_worker_nodes(self):
        """Get "worker nodes" -- that is, nodes on which we can schedule user
        workloads. In a minimal cluster, this will actually be the control
        plane nodes."""
        nodes = self.get("v1", "Node", label_selector="node-role.kubernetes.io/worker")
        if not nodes.items:
            nodes = self.get(
                "v1", "Node", label_selector="node-role.kubernetes.io/control-plane"
            )
        if not nodes.items:
            nodes = self.get(
                "v1", "Node", label_selector="node-role.kubernetes.io/master"
            )

        return nodes.items

def make_template_fixture(basename,):
    """Given a template name, return a function that when called
    will render the template."""

    def func(kube, manifests, testid, testimage, request):
        def render_template(**kwargs):
            tmpl = manifests.get_template(f"{basename}.yaml")
            return yaml.safe_load_all(
                tmpl.render(testid=testid, testimage=testimage, testname=request.node.originalname, **kwargs)
            )

        return render_template

    return pytest.fixture(func)


def make_resource_fixture(basename, **kwargs):
    """Given a template name, render the template, create the corresponding
    objects, and return them to the caller. Clean up all the objects when the
    test is complete."""

    def func(kube, manifests, testid, testimage, request):
        template = manifests.get_template(f"{basename}.yaml")
        with kube.manage(
            yaml.safe_load_all(
                template.render(testid=testid, testimage=testimage, testname=request.node.originalname, **kwargs)
            )
        ) as objects:
            yield objects

    return pytest.fixture(func)


def assert_conditions(obj, conditionMap):
    """Given an object and a map of {<condition_type>: <expected_value>},
    assert that the object has all the expected conditions."""

    for condition in obj.status.conditions:
        if condition.type in conditionMap:
            assert (
                condition.status == conditionMap[condition.type]
            ), f"{obj.kind} {obj.metadata.name} condition {condition.type} is {condition.status}: {condition.message}"

def get_conditions(obj):
    return {condition['type']: condition for condition in obj.status.conditions}


def get_condition(obj, ctype):
    return get_conditions(obj)[ctype]


