World Colors:
```
{% for group_name, color_group in color_groups.items %}{% if group_name %}{{ group_name|title|stringformat:"25s" }}
{% endif %}{% for color in color_group %}{% include 'boundlexx/notifications/exoworld_color.md' %}{% endfor %}{% if group_name == "grass" %}```%SPLIT_MESSAGE%```{% else %}
{% endif %}{% endfor %}
```
