{% load utils %}
{% if world.is_exo %}
     {% if color.is_new_exo %}
      - ![|25x25]({{ icons.exo_color_new }})
     {% else %}
          {% if color.is_perm %}
          - **_{% if color.first_world and color.first_world.forum_url %}[![{{ color.first_world.text_name }}|25x25]({{ world_images|key:color.first_world.id }})]({{ color.first_world.forum_url }}){% else %}![|25x25](upload://hRlPcEQgOBNrB5q38AT7n1cPleB.png){% endif %}_**
          {% else %}
               {% if color.transform_first_world or color.transform_last_exo or color.days_since_exo %} -{% endif %}
               {% if color.transform_first_world or color.transform_last_exo %}
                ![|25x25]({{ icons.by_recipe }})
               {% endif %}
               {% if color.days_since_exo %}
                    {% if color.transform_first_world or color.transform_last_exo %}-{% endif %}
                     ![|20x20]({{ icons.timelapse }})**_{% if color.last_exo and color.last_exo.forum_url %}[{{ color.days_since_exo }}]({{ color.last_exo.forum_url }}){% else %}{{ color.days_since_exo }}{% endif %}_**
               {% endif %}
          {% endif %}
     {% endif %}
{% else %}
     {% if world.is_sovereign and not world.is_creative %}
          {% if color.is_perm %}
           - **_{% if color.first_world and color.first_world.forum_url %}[![{{ color.first_world.text_name }}|25x25]({{ world_images|key:color.first_world.id }})]({{ color.first_world.forum_url }}){% else %}![|25x25](upload://hRlPcEQgOBNrB5q38AT7n1cPleB.png){% endif %}_**
          {% else %}
               {% if color.is_new and color.is_default %}- ![|25x25]({{ icons.exo_color_new }}){% endif %}
          {% endif %}
     {% endif %}
{% endif %}
