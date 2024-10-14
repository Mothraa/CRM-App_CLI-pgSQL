from my_app.models import User  # , RoleType

# permissions sous forme de dict, alternative plus évoluée => casbin

ROLES_PERMISSIONS = {
    "admin": [
        "add-user",
        "update-user",
        "user-modify-email",
        "user-modify-password",
        "user-modify-role",
        "delete-user",
    ],
    "manage": [
    ],
    "sales": [
    ],
    "support": [
    ],
}


def has_permission(user: User, permission: str) -> bool:
    """Verify if user as the specified permission"""
    if permission not in ROLES_PERMISSIONS.get(user.role, []):
        raise PermissionError(f"User don't have permission: {permission}")
    return True


def has_any_permission(user: User, permissions: list) -> bool:
    """Verify if user as AT LEAST ONE of specified permissions"""
    if not any(permission in ROLES_PERMISSIONS.get(user.role, []) for permission in permissions):
        raise PermissionError(f"User don't have ANY of these permissions: {', '.join(permissions)}")
    return True


def has_all_permissions(user: User, permissions: list) -> bool:
    """Verify if user as ALL of specified permissions"""
    if not all(permission in ROLES_PERMISSIONS.get(user.role, []) for permission in permissions):
        raise PermissionError(f"User don't have ALL of these permissions: {', '.join(permissions)}")
    return True
