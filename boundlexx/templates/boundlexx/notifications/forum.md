{% load humanize tz utils %}{% if world.image %}![|300x300]({{ world.image.url }}){% else %}![|300x300]({{ icons.world_image }}){% endif %}{% if world.is_sovereign %}
**-------------------------[Sovereign Details]------------------------**
![|30x30]({{ icons.name }}) Owner : **{% if username %}{{ username }}{% else %}ADD YOUR NAME HERE{% endif %}**
![|30x30]({{ icons.name }}) Permissions : **{% if perms %}{% if perms.can_visit %}Can{% else %}No{% endif %} Visit | {% if perms.can_edit %}Can{% else %}No{% endif %} Edit | {% if perms.can_claim %}Can{% else %}No{% endif %} Claim{% else %}Can|No Visit - Can|No Edit - Can|No Claim{% endif %}**{% endif %}
**--------------------------[🌍 World Details]-------------------------**
![|30x30]({{ icons.name }}) Name : **{{ world.display_name }}**
![|30x30]({{ icons.name }}) ID: **{{ world.id }}**
![|30x30]({{ icons.type|key:world.world_type }}) Type : **{{ world.get_world_type_display }}**
![|30x30]({{ icons.tier }}) Tier : **{{ world.get_tier_display }}**
![|30x30]({{ icons.atmosphere|key:world.atmosphere_name }}) Atmosphere : {% if world.protection %}**{{ world.protection }}**{% else %}Normal{% endif %}
![|30x30]({{ icons.name }}) Size : **{{ world.display_size }}**
![|30x30]({{ icons.liquid }}) Liquid : **▲ {{ world.surface_liquid }}** | ▼ **{{ world.core_liquid }}**{% if world.assignment %}
![|30x30]({{ icons.server }}) Region : **{{ world.get_region_display }}**
**------------------------[🧭 Distance Details]------------------------**
![|30x30]({{ icons.blinksec }}) **{{ world.assignment_distance }} blinksecs** _from_ **_{% if world.assignment.forum_url %}[{{ world.assignment.display_name }}]({{ world.assignment.forum_url }}){% else %}{{ world.assignment.display_name }}{% endif %}_**{% if not world.is_creative %}
![|30x30]({{ icons.warpcost }}) Warp Cost : **{{ world.assignment_cost }}c**{% endif %}{% if world.is_sovereign %}
![|30x30]({{ icons.name }}) Portals : **{% if directions %}{{ directions }}{% else %}ADD PORTALS HERE{% endif %}**{% endif %}{% endif %}{% if world.start %}
**--------------------------[⏱ Time Details]--------------------------**
![|30x30]({{ icons.lifetime }}) Appeared **[date={{ world.start|utc|date:"Y-m-d" }} time={{ world.start|utc|date:"G:i:s" }} format="LLL" timezones="UTC"]**{% if world.end %}
![|30x30]({{ icons.lifetime }}) Last until **[date={{ world.end|utc|date:"Y-m-d" }} time={{ world.end|utc|date:"G:i:s" }} format="LLL" timezones="UTC"]**{% endif %}{% endif %}
**--------------------------------------------------------------------**{% if color_groups %}
[details="Blocks Colors"]
**--------------------------------------------------------------------**{% if not world.is_perm %}
![|25x25]({{ icons.exo_color_new }}) **:** _New Color to this date_{% if world.is_exo %}
![|25x25]({{ icons.by_recipe }}) **:** _Can be obtained by **Recipe/Transmutation**_
![|20x20]({{ icons.timelapse }})**_[∞]()_** **:** _Obtained on Homeworld_
![|20x20]({{ icons.timelapse }})**_[>= 0]()_** **:** _Exo Exclusive **last occurrence** in **Days**_{% endif %}{% endif %}
**--------------------------------------------------------------------**

{% for group_name, color_group in color_groups.items %}{% if group_name %}

_**[{{ group_name|title }}]**_
{% endif %}{% for color in color_group %}∟![|30x30]({{ icons.colors|key:color.color.game_id }}) **- {{ color.item.english }} -** _{{ color.color.game_id }} {{ color.color.default_name }}_{% include 'boundlexx/notifications/forum_color_icons.md' %}
{% endfor %}{% endfor %}
[/details]
**--------------------------------------------------------------------**{% endif %}{% if embedded_resources %}
[details="Initial Resources"]
**---------------------[Embedded World Resources]---------------------**
<table>
<tr><th>Rank</th><th>Resource Name</th><th>Absolute Count</th><th>Percentage</th></tr>{% for resource in embedded_resources %}
<tr><td>{{ forloop.counter }}</td><td>{{ resource.item.english }}</td><td>{{ resource.count|intcomma }}</td><td>{{ resource.percentage }}%</td>{% endfor %}
</table>


**----------------------[Surface World Resources]---------------------**
<table>
<tr><th>Rank</th><th>Resource Name</th><th>Absolute Count</th><th>Percentage</th></tr>{% for resource in surface_resources %}
<tr><td>{{ forloop.counter }}</td><td>{{ resource.item.english }}</td><td>{{ resource.count|intcomma }}</td><td>{{ resource.percentage }}%</td>{% endfor %}
</table>
[/details]{% endif %}
