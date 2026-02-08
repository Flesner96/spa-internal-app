from accounts.permissions import Capability


def can_view_notebook(user) -> bool:
    return user.can(Capability.VIEW_NOTEBOOK)


def can_post_message(user) -> bool:
    return user.can(Capability.POST_NOTEBOOK)


def can_edit_message(user, message) -> bool:
    return (
        message.author == user
        or user.can(Capability.EDIT_NOTEBOOK)
    )
