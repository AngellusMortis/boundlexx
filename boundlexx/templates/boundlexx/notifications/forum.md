{% load humanize tz utils %}{% if world.image %}![|300x300]({{ world.image.url }}){% else %}![|300x300]({{ icons.world_image }}){% endif %}
**-------------------------------------------------------------------**{% if world.is_sovereign %}
![|30x30]({{ icons.name }}) Owner : **ADD YOUR NAME HERE**
![|30x30]({{ icons.name }}) Permissions : **Can|No Warp - Can|No Gather - Can|No Plot**
**-------------------------------------------------------------------**{% endif %}
![|30x30]({{ icons.name }}) Name : **{{ world.display_name }}**
![|30x30]({{ icons.type|key:world.world_type }}) Type : **{{ world.get_world_type_display }}**
![|30x30]({{ icons.tier }}) Tier : **{{ world.get_tier_display }}**{% if world.protection_points %}
![|30x30]({{ icons.atmosphere|key:world.atmosphere_name }}) Atmosphere : **{{ world.protection }}**{% else %}
![|30x30]({{ icons.atmosphere.Normal }}) Atmosphere : **Normal**{% endif %}
![|30x30]({{ icons.name }}) Size : **{{ world.display_size }}**
![|30x30]({{ icons.liquid }}) Surface : **{{ world.surface_liquid }}**
![|30x30]({{ icons.liquid }}) Underground : **{{ world.core_liquid }}**
**-------------------------------------------------------------------**{% if world.assignment %}{% if world.assignment.forum_url %}
![|30x30]({{ icons.blinksec }}) **{{ world.assignment_distance }} blinksecs** _from_ **_[{{ world.assignment.display_name }}]({{ world.assignment.forum_url }})_**{% else %}
![|30x30]({{ icons.blinksec }}) **{{ world.assignment_distance }} blinksecs** _from_ **_{{ world.assignment.display_name }}_**{% endif %}
![|30x30]({{ icons.warpcost }}) Warp Cost : **{{ world.assignment_cost }}c**{% if world.is_sovereign %}
![|30x30]({{ icons.name }}) Portals : **ADD PORTALS HERE**{% endif %}
**-------------------------------------------------------------------**{% endif %}{% if world.start %}
![|30x30]({{ icons.lifetime }}) Appeared **[date={{ world.start|utc|date:"Y-m-d" }} time={{ world.start|utc|date:"G:i:s" }} format="LLL" timezones="UTC"]**{% endif %}{% if world.end %}
![|30x30]({{ icons.lifetime }}) Last until **[date={{ world.end|utc|date:"Y-m-d" }} time={{ world.end|utc|date:"G:i:s" }} format="LLL" timezones="UTC"]**{% endif %}
![|30x30]({{ icons.server }}) Server : **{{ world.get_region_display }}**
**-------------------------------------------------------------------**{% if color_groups %}
[details="Blocks Colors"]
**-------------------------------------------------------------------**
![|25x25]({{ icons.exo_color_new }}) **:** _New Color to this date_
![|25x25]({{ icons.by_recipe }}) **:** _Can be obtained by **Recipe/Transmutation**_
![|20x20]({{ icons.timelapse }})**_[∞]()_** **:** _Obtained on Homeworld_
![|20x20]({{ icons.timelapse }})**_[>= 0]()_** **:** _Exo Exclusive **last occurrence** in **Days**_
**-------------------------------------------------------------------**

{% for group_name, color_group in color_groups.items %}{% if group_name %}

_**[{{ group_name|title }}]**_
{% endif %}{% for color in color_group %}∟![|30x30]({{ icons.colors|key:color.color.game_id }}) **- {{ color.item.english }} -** _{{ color.color.game_id }} {{ color.color.default_name }}_ -{% if world.is_exo %}{% if color.exist_on_perm %} ![|20x20]({{ icons.timelapse }})**_[∞]()_**{% else %}{% if color.is_new_color %}![|25x25]({{ icons.exo_color_new }}){% else %}{% if color.exist_via_transform %} ![|25x25]({{ icons.by_recipe }}){% endif %}{% if color.days_since_last %} ![|20x20]({{ icons.timelapse }}) **_[{{ color.days_since_last }}]()_**{% endif %}{% endif %}{% endif %}{% endif %}
{% endfor %}{% endfor %}
[/details]
**-------------------------------------------------------------------**{% endif %}{% if embedded_resources %}
[details="Initial Resources"]
_**[Embedded World Resources]**_
<table>
<tr><th>Rank</th><th>Resource Name</th><th>Absolute Count</th><th>Percentage</th></tr>{% for resource in embedded_resources %}
<tr><td>{{ forloop.counter }}</td><td>{{ resource.item.english }}</td><td>{{ resource.count|intcomma }}</td><td>{{ resource.percentage }}%</td>{% endfor %}
</table>

_**[Surface World Resources]**_
<table>
<tr><th>Rank</th><th>Resource Name</th><th>Absolute Count</th><th>Percentage</th></tr>{% for resource in surface_resources %}
<tr><td>{{ forloop.counter }}</td><td>{{ resource.item.english }}</td><td>{{ resource.count|intcomma }}</td><td>{{ resource.percentage }}%</td>{% endfor %}
</table>
[/details]{% endif %}
