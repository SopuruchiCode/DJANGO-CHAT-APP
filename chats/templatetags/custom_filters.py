from django import template

register = template.Library()


@register.filter
def get_item(dictionary, key):
    return dictionary.get(key, {})

@register.filter
def get_attr(obj, attr):
    return getattr(obj, attr, "Attribute Does not exist")

@register.filter
def get_method(obj, method):
    method = getattr(obj, method, None)
    if method and callable(method):
        return method()
        