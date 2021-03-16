from django import template


register = template.Library()


@register.filter
def get_obj_attr(obj, attr):
    if obj is not None:
        return getattr(obj, attr.lower())
    else:
        return "---"


@register.filter
def get_fields(obj):
    return [(field.verbose_name, field.value_to_string(obj)) for field in obj._meta.fields]