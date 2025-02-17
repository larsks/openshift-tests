{% import "macros" as macros %}
# Test results

Test run at: {{ testsuite['@timestamp'] }}

## Summary

| Total | Passed | Skipped | Failed | Errors |
|-------|--------|---------|--------|--------|
| {{testsuite['@tests']}} | {{tests_passed|length}} | {{ tests_skipped|length }} | {{tests_failure|length}} | {{tests_error|length}} |

{% if tests_failure %}
## Failed

{% for testcase in tests_failure -%}
{{ macros.testcase_result(":red_circle:", testcase, show_properties) }}
{%- endfor -%}
{% endif %}

{% if not only_failures %}
{% if tests_skipped %}
## Skipped

{% for testcase in tests_skipped -%}
{{ macros.testcase_result(":orange_circle:", testcase, show_properties) }}
{%- endfor -%}
{% endif %}

{% if tests_passed %}
## Passed

{% for testcase in tests_passed -%}
{{ macros.testcase_result(":green_circle:", testcase, show_properties) }}
{%- endfor -%}
{% endif %}

{% if tests_error %}
## Errors

{% for testcase in tests_error -%}
{{ macros.testcase_result(":black_circle:", testcase, show_properties) }}
{%- endfor -%}
{% endif %}
{% endif %}
