from django import template

register = template.Library()


@register.simple_tag(takes_context=True)
def has_cap(context, capability):
    user = context["request"].user
    return user.can(capability)