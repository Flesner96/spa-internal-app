from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.models import BaseUserManager, UserManager

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

    objects = UserManager()


    # =====================
    # PERMISSIONS / RBAC
    # =====================

    @property
    def role_codes(self) -> set[str]:
        
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
        
        return self.has_role("SysA")

    @property
    def is_sa_supervisor(self) -> bool:
        
        return (
            self.area
            and self.area.code == "SA"
            and self.has_role("ASup")
        )

    def can(self, capability: str) -> bool:
        
        from .permissions import user_has_capability

        if self.is_sys_admin:
            return True

        return user_has_capability(self, capability)



class UserRole(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    role = models.ForeignKey(Role, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('user', 'role')



class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("Email is required")

        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        return self.create_user(email, password, **extra_fields)
