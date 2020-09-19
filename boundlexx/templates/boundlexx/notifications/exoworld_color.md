{{ color.item.english|stringformat:"25s" }}: {{ color.color.default_name }} ({{ color.color.game_id }}){% if color.is_new_color %} NEW{% else %}{% if color.exist_via_transform %} TRANSFORM{% endif %}{% if color.days_since_last %} Days: {{ color.days_since_last }}{% endif %}{% endif %}



{% if world.is_exo %}
    {% if color.is_new_exo_color %}
        NEW
    {% else %}
        {% if not color.first_world %}
            {% if color.exist_via_transform %}
                TRANS
            {% endif %}
            {% if color.exist_via_transform %}
                EXOTRANS
            {% endif %}
            {% if color.days_since_last %}
                Days: {{ color.days_since_last }}
            {% endif %}
        {% endif %}
    {% endif %}
{% else %}
    {% if world.is_sovereign and not world.is_creative %}
        {% if color.is_new_exo_color %}
            NEW
        {% endif %}
    {% endif %}
{% endif %}
