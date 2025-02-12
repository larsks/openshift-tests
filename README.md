# OpenShift Tests

To run these tests:

1. Clone the repository.

    ```
    git clone https://github.com/ocp-on-nerc/openshift-tests
    cd openshift-tests
    ```

1. Set up the Python environment:

    ```
    uv sync
    ```

1. Run the tests. If you are not running as a cluster admin, provide a namespace name in which you are able to create resources:

    ```
    uv run pytest --namespace mynamespace
    ```

You can run the tests in parallel by specifying `-n auto` on the `pytest` command line.

