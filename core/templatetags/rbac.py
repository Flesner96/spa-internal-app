from django import template

register = template.Library()


@register.simple_tag(takes_context=True)
def has_cap(context, capability):
    request = context.get("request")

    if not request:
        return False

    return request.user.can(capability)


@register.filter
def can(user, capability):
    return user.can(capability)