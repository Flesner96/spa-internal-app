def is_sa_area(user) -> bool:
    return bool(user.area and user.area.code == "SA")


def can_edit_saunas(user) -> bool:

    if user.is_sys_admin:
        return True

    return (
        is_sa_area(user)
        and user.has_any_role("BS", "ASup")
    )


def can_import_saunas(user) -> bool:
   
    if user.is_sys_admin:
        return True

    return (
        is_sa_area(user)
        and user.has_role("ASup")
    )
