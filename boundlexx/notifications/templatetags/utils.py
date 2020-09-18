from django import template

register = template.Library()


@register.filter
def key(value, key_name):
    return value.get(key_name)
