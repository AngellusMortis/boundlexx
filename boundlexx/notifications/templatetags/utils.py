from django import template

register = template.Library()


@register.filter
def key(value, key_name):
    return value.get(str(key_name))


@register.filter
def replace(value, string_to_remove):
    string_to_remove = " " + string_to_remove
    return value.lower().replace(string_to_remove.lower(), "").strip().title()
