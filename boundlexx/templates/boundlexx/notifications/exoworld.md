{% load humanize %}A new exoworld world as appeared!

Name: **{{ world.display_name }}**

World Details:
```
ID: {{ world.name }} ({{ world.id }})
Server: {{ world.address }}
Start: {{ world.start|naturaltime }} ({{ world.start }} UTC)
End: {{ world.end|naturaltime }} ({{ world.end }} UTC)
Tier: {{ world.get_tier_display }}
Server Region: {{ world.get_region_display }}
World Type: {{ world.get_world_type_display }}
World Size (16-block chunks): {{ world.size }}
Number of Regions: {{ world.number_of_regions }}
Closest Planet: {{ world.assignment }} @{{ world.assignment_distance }} blinksecs
Surface Liquid: {{ world.surface_liquid }}
Core Liquid: {{ world.core_liquid }}
```

World Resources:
```{% for resource in resources %}
{{ resource.item.english|stringformat:"25s" }}: {{ resource.count|intcomma }}{% endfor %}
```{% if colors %}%SPLIT_MESSAGE%
{% include 'boundlexx/notifications/exoworld_colors.md' %}{% endif %}