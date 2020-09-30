{% load humanize tz utils %}{% if world.image %}![|300x300]({{ world.image.url }}){% else %}![{{ world.display_name }}|300x300]({{ icons.world_image }}){% endif %}{% if world.is_sovereign %}
**-------------------[Sovereign Details]-------------------**
![|30x30]({{ icons.owner }}) Owner : **{% if username %}@{{ username }}{% else %}ADD YOUR NAME HERE{% endif %}**
![|30x30]({{ icons.permissions }}) Permissions : **{% if world.has_perm_data %}{% if world.is_public %}![Yes|25x25]({{ icons.yes }}){% else %}![No|25x25]({{ icons.no }}){% endif %} Visit | {% if world.is_public_edit %}![Yes|25x25]({{ icons.yes }}){% else %}![No|25x25]({{ icons.no }}){% endif %} Edit | {% if world.is_public_claim %}![Yes|25x25]({{ icons.yes }}){% else %}![No|25x25]({{ icons.no }}){% endif %} Claim{% else %}{% if perms %}{% if perms.can_visit %}![Yes|25x25]({{ icons.yes }}){% else %}![No|25x25]({{ icons.no }}){% endif %} Visit | {% if perms.can_edit %}![Yes|25x25]({{ icons.yes }}){% else %}![No|25x25]({{ icons.no }}){% endif %} Edit | {% if perms.can_claim %}![Yes|25x25]({{ icons.yes }}){% else %}![No|25x25]({{ icons.no }}){% endif %} Claim{% else %}![Yes|25x25]({{ icons.yes }})|![No|25x25]({{ icons.no }}) Visit - ![Yes|25x25]({{ icons.yes }})|![No|25x25]({{ icons.no }}) Edit - ![Yes|25x25]({{ icons.yes }})|![No|25x25]({{ icons.no }}) Claim{% endif %}{% endif %}**{% if perms and comptactness != None %}
![|30x30]({{ icons.permissions }}) Beacon Compactness : **{% if compactness %}![Yes|25x25]({{ icons.yes }}){% else %}![No|25x25]({{ icons.no }}){% endif %}**{% endif %}{% endif %}
**--------------------[🌍 World Details]--------------------**
![|30x30]({{ icons.name }}) ID : **{{ world.id }}**
![|30x30]({{ icons.name }}) Name : **{{ world.display_name }}**{% if world.special_type %}
![|30x30]({{ icons.name }}) Special Type : **{{ world.get_special_type_display }}**{% endif %}
![|30x30]({{ icons.type|key:world.world_type }}) Type : **{{ world.get_world_type_display }}**
![|30x30]({{ icons.tier }}) Tier : **{{ world.get_tier_display }}**
![|30x30]({{ icons.atmosphere|key:world.atmosphere_name }}) Atmosphere : {% if world.protection %}**{{ world.protection }}**{% else %}Normal{% endif %}
![|30x30]({{ icons.name }}) Size : **{{ world.display_size }}**
![|30x30]({{ icons.liquid }}) Liquid : **▲ {{ world.surface_liquid }}** | ▼ **{{ world.core_liquid }}**{% if world.assignment %}
![|30x30]({{ icons.server }}) Region : **{{ world.get_region_display }}**
**------------------[🧭 Distance Details]------------------**
![|30x30]({{ icons.blinksec }}) **{{ world.assignment_distance }} blinksecs** _from_ **_{% if world.assignment.forum_url %}[{{ world.assignment.display_name }}]({{ world.assignment.forum_url }}){% else %}{{ world.assignment.display_name }}{% endif %}_**{% if not world.is_creative %}
![|30x30]({{ icons.warpcost }}) Warp Cost : **{{ world.assignment_cost }}c**{% endif %}{% if world.is_sovereign %}
![|30x30]({{ icons.portal }}) Portals : **{% if directions %}{{ directions }}{% else %}ADD PORTALS HERE{% endif %}**{% endif %}{% endif %}{% if world.start %}
**---------------------[⏱ Time Details]---------------------**
![|30x30]({{ icons.lifetime }}) Appeared **[date={{ world.start|utc|date:"Y-m-d" }} time={{ world.start|utc|date:"G:i:s" }} format="LLL" timezones="UTC"]**{% if world.end %}
![|30x30]({{ icons.lifetime }}) Last until **[date={{ world.end|utc|date:"Y-m-d" }} time={{ world.end|utc|date:"G:i:s" }} format="LLL" timezones="UTC"]**{% endif %}{% if will_renew != None %}{% if will_renew %}
![|30x30]({{ icons.lifetime }}) Will Renew : ![Yes|25x25]({{ icons.yes }}){% else %}
![|30x30]({{ icons.lifetime }}) Will Renew : ![No|25x25]({{ icons.no }}){% endif %}{% endif %}{% endif %}
**-------------------------------------------------------------------**{% if default_color_groups %}
[details="Default Blocks Colors"]
**-------------------------------------------------------------------**
![|25x25]({{ icons.exo_color_new }}) **:** _New Color to this date_
[![|25x25]({{ icons.homeworld|key:1 }})]() **:** _Obtained on Homeworld (clickable)_
**-------------------------------------------------------------------**

{% for group_name, color_group in default_color_groups.items %}{% if group_name %}

_**[{{ group_name|title }}]**_
{% endif %}{% for color in color_group %}∟![|30x30]({{ icons.colors|key:color.color.game_id }}) **- {{ color.item.english|replace:group_name }} -** _{{ color.color.game_id }} {{ color.color.default_name }}_{% include 'boundlexx/notifications/forum_color_icons.md' %}
{% endfor %}{% endfor %}
[/details]
**-------------------------------------------------------------------**{% endif %}{% if world.special_type == 1 %}
**Block Colors** : This world is a "Color-Cycling" world. That means the colors change at random.
**-------------------------------------------------------------------**{% else %}{% if color_groups %}
[details="{% if world.is_sovereign %}Current {% endif %}Blocks Colors"]
**-------------------------------------------------------------------**{% if not world.is_perm %}{% if world.is_exo %}
![|25x25]({{ icons.exo_color_new }}) **:** _New Color to this date_
![|25x25]({{ icons.by_recipe }}) **:** _Can be obtained by **Recipe/Transmutation**_{% endif %}
[![|25x25]({{ icons.homeworld|key:1 }})]() **:** _Obtained on Homeworld (clickable)_{% if world.is_exo %}
![|20x20]({{ icons.timelapse }})**_[>= 0]()_** **:** _Exo Exclusive **last occurrence** in **Days**_{% endif %}{% endif %}
**-------------------------------------------------------------------**

{% for group_name, color_group in color_groups.items %}{% if group_name %}

_**[{{ group_name|title }}]**_
{% endif %}{% for color in color_group %}∟![|30x30]({{ icons.colors|key:color.color.game_id }}) **- {{ color.item.english|replace:group_name }} -** _{{ color.color.game_id }} {{ color.color.default_name }}_{% include 'boundlexx/notifications/forum_color_icons.md' %}
{% endfor %}{% endfor %}
[/details]
**-------------------------------------------------------------------**{% endif %}{% endif %}{% if embedded_resources %}
[details="Initial Resources"]
**------------[Embedded World Resources]------------**
<table>
<tr><th>Rank</th><th>Resource Name</th><th>Absolute Count</th><th>Percentage</th><th>Average Per Chunk</th></tr>{% for resource in embedded_resources %}
<tr><td>{{ forloop.counter }}</td><td>{{ resource.item.english }}</td><td>{{ resource.count|intcomma }}</td><td>{{ resource.percentage }}%</td><td>{{ resource.average_per_chunk }}</td>{% endfor %}
</table>


**--------------[Surface World Resources]--------------**
<table>
<tr><th>Rank</th><th>Resource Name</th><th>Absolute Count</th><th>Percentage</th><th>Average Per Chunk</th></tr>{% for resource in surface_resources %}
<tr><td>{{ forloop.counter }}</td><td>{{ resource.item.english }}</td><td>{{ resource.count|intcomma }}</td><td>{{ resource.percentage }}%</td><td>{{ resource.average_per_chunk }}</td>{% endfor %}
</table>
[/details]{% endif %}
