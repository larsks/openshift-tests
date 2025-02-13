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
    marker = ":green_circle:"
    if "failure" in testcase:
        marker = ":red_circle:"
    elif "skipped" in testcase:
        marker = ":orange_circle:"

    return f'{marker} `{testcase['@classname']}`::**`{testcase['@name']}`**'


@filter
def message(testcase):
    action = testcase.get("skipped", testcase.get("failure"))
    if action:
        return action["@message"]


@filter
def failed(tests):
    return [test for test in tests if "failure" in test]


@filter
def skipped(tests):
    return [test for test in tests if "skipped" in test]


@filter
def passed(tests):
    return [test for test in tests if "skipped" not in test and "failure" not in test]


def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument("--only-failures", "-f", action="store_true")
    p.add_argument("--no-properties", "-p", dest='show_properties', default=True, action='store_false')
    p.add_argument("--output", "-o")
    p.add_argument("results")
    return p.parse_args()


def main():
    args = parse_args()
    tmpl = env.get_template("results.md")
    with open(args.results) as fd:
        data = fd.read()

    results = xmltodict.parse(data, force_list=['testcase', 'property'])

    with open(args.output, "w") if args.output else sys.stdout as fd:
        fd.write(tmpl.render(testsuite=results["testsuites"]["testsuite"], only_failures=args.only_failures, show_properties=args.show_properties))


if __name__ == "__main__":
    main()
