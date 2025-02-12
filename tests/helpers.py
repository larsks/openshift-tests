import time

import jsonpath_ng as jsonpath
import yaml
from kubernetes import client, config, dynamic
from pytest import fixture


class KubeHelper:
    """This is a help class that makes interacting with the kubernetes dynamic api somewhat easier"""

    def __init__(self, testid, namespace="default"):
        self.testid = testid
        self.namespace = namespace
        self.apiclient = client.ApiClient()
        self.dynclient = dynamic.DynamicClient(self.apiclient)

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
                    f'expression {expr} for {obj.kind} "{obj.metadata.name}" failed to reach value {value}'
                )

            time.sleep(1)

        return obj


def make_template_fixture(basename, **kwargs):
    """Read a jinja template from the `manifests/<basename>.yaml` file, render
    the template, and then create all the objects described in the manifest.
    The template will always receive values for `testid` and `testimage`; if
    you provide any additional values in `kwargs`, they will be provided to the
    template.

    When the test is complete, delete all the objects that we created."""

    def func(kube, manifests, testid, testimage):
        template = manifests.get_template(f"{basename}.yaml")
        specs = yaml.safe_load_all(
            template.render(testid=testid, testimage=testimage, **kwargs)
        )
        objects = kube.create_objects(specs)
        yield objects
        kube.delete_objects(objects)

    return fixture(func)


def assert_conditions(obj, conditionMap):
    """Given an object and a map of {<condition_type>: <expected_value>},
    assert that the object has all the expected conditions."""

    for condition in obj.status.conditions:
        if condition.type in conditionMap:
            assert (
                condition.status == conditionMap[condition.type]
            ), f"{obj.kind} {obj.metadata.name} condition {condition.type} is {condition.status}: {condition.message}"
