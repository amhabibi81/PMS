from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _


class User(AbstractUser):
    """Custom user with a single global role.

    The global role caps the maximum privilege the user can be granted in any project.
    Per-project privileges are stored on ProjectMembership.
    """

    class Role(models.TextChoices):
        ADMIN = "Admin", _("Admin")
        PROJECT_MANAGER = "ProjectManager", _("Project Manager")
        MEMBER = "Member", _("Team Member")

    email = models.EmailField(_("email address"), unique=True)
    role = models.CharField(
        _("role"), max_length=20, choices=Role.choices, default=Role.MEMBER
    )

    class Meta:
        ordering = ["username"]
        verbose_name = _("user")
        verbose_name_plural = _("users")

    def __str__(self) -> str:
        full = self.get_full_name()
        return f"{full} ({self.role})" if full else f"{self.username} ({self.role})"

    @property
    def is_admin(self) -> bool:
        return self.role == self.Role.ADMIN

    @property
    def is_project_manager(self) -> bool:
        return self.role in (self.Role.ADMIN, self.Role.PROJECT_MANAGER)
