from accounts.permissions import Capability


def can_view_classes(user):
    return user.can(Capability.VIEW_CLASSES)

def can_manage_classes(user):
    return user.can(Capability.MANAGE_CLASSES)