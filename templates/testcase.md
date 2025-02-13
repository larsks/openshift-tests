- {{ testcase|style_name }}
{% if testcase|message %}

  {{ testcase|message|wordwrap(75)|indent(2) }}
{% endif %}
{% if show_properties and testcase.get('properties', {}).get('property') %}

  | Property | Value |
  |----------|-------|
{% for property in testcase['properties'].get('property', []) %}
  | {{ property['@name'] }} | {{ property['@value'] }} |
{% endfor %}
{% endif %}


