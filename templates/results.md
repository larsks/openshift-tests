# Test results

Test run at: {{ testsuite['@timestamp'] }}

## Summary

| Total | Passed | Skipped | Failed | Errors |
|-------|--------|---------|--------|--------|
| {{testsuite['@tests']}} | {{testsuite['@tests']|int - testsuite['@skipped']|int - testsuite['@failures']|int - testsuite['@errors']|int}} | {{testsuite['@skipped']}} | {{testsuite['@failures']}} | {{testsuite['@errors']}} |

## Failed

{% for testcase in testsuite.testcase|failed -%}
{% include "testcase.md" %}
{%- endfor -%}

{% if not only_failures %}
## Skipped

{% for testcase in testsuite.testcase|skipped -%}
{% include "testcase.md" %}
{%- endfor -%}

## Passed

{% for testcase in testsuite.testcase|passed -%}
{% include "testcase.md" %}
{%- endfor -%}
{% endif %}
