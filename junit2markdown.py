import argparse
import sys

import jinja2
import xmltodict

env = jinja2.Environment(loader=jinja2.FileSystemLoader("templates"), trim_blocks=True)


def filter(func):
    env.filters[func.__name__] = func
    return func


@filter
def style_name(testcase):
    return f'`{testcase['@classname']}`::**`{testcase['@name']}`**'


@filter
def message(testcase):
    action = testcase.get("skipped", testcase.get("failure", testcase.get("error")))
    if action:
        return action["@message"]


def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument("--only-failures", "-f", action="store_true")
    p.add_argument(
        "--properties", "-p", dest="show_properties", default=False, action="store_true"
    )
    p.add_argument("--output", "-o")
    p.add_argument("results")
    return p.parse_args()


def main():
    args = parse_args()
    tmpl = env.get_template("results.md")
    with open(args.results) as fd:
        data = fd.read()

    results = xmltodict.parse(data, force_list=["testcase", "property"])
    tests_failure = []
    tests_skipped = []
    tests_passed = []
    tests_error = []
    for testcase in results["testsuites"]["testsuite"]["testcase"]:
        if "failure" in testcase:
            tests_failure.append(testcase)
        elif "skipped" in testcase:
            tests_skipped.append(testcase)
        elif "error" in testcase:
            tests_error.append(testcase)
        else:
            tests_passed.append(testcase)

    with open(args.output, "w") if args.output else sys.stdout as fd:
        fd.write(
            tmpl.render(
                tests_failure=tests_failure,
                tests_skipped=tests_skipped,
                tests_error=tests_error,
                tests_passed=tests_passed,
                testsuite=results["testsuites"]["testsuite"],
                only_failures=args.only_failures,
                show_properties=args.show_properties,
            )
        )


if __name__ == "__main__":
    main()
