from django.db import models
from django.contrib.auth.models import AbstractUser

class Area(models.Model):
    name = models.CharField(max_length=100)
    code = models.CharField(
        max_length=30,
        unique=True
    )
    def __str__(self):
        return self.name
    

class Role(models.Model):
    code = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name
    

class User(AbstractUser):
    username = None
    email = models.EmailField(unique=True)

    area = models.ForeignKey(Area, on_delete=models.PROTECT)
    phone = models.CharField(max_length=20, blank=True)
    must_change_password = models.BooleanField(default=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    # =====================
    # PERMISSIONS / RBAC
    # =====================

    @property
    def role_codes(self) -> set[str]:
        """
        Cached set of role codes assigned to the user.
        """
        if not hasattr(self, "_cached_role_codes"):
            self._cached_role_codes = set(
                self.userrole_set.values_list("role__code", flat=True)
            )
        return self._cached_role_codes

    def has_role(self, code: str) -> bool:
        return code in self.role_codes

    def has_any_role(self, *codes: str) -> bool:
        return any(code in self.role_codes for code in codes)

    @property
    def is_sys_admin(self) -> bool:
        """
        Semantic helper — SysA is a global override role.
        """
        return self.has_role("SysA")

    @property
    def is_sa_supervisor(self) -> bool:
        """
        Domain-specific helper (business rule).
        """
        return (
            self.area
            and self.area.code == "SA"
            and self.has_role("ASup")
        )

    def can(self, capability: str) -> bool:
        """
        Capability-based RBAC check.
        """
        from .permissions import user_has_capability
        return user_has_capability(self, capability)



class UserRole(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    role = models.ForeignKey(Role, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('user', 'role')



