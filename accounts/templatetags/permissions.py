from django import template

register = template.Library()

@register.filter
def can(user, capability):
    return user.can(capability)