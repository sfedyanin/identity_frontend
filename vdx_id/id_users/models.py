import logging
from django.db import models
from django.contrib.auth.models import AbstractUser, UserManager

logger = logging.getLogger('vdx_id.%s' % __name__)


class VdxIdUserManager(UserManager):
    pass


class VdxIdUser(AbstractUser):
    """Custom UserModel to handle auth and special functionality"""
    first_name = models.CharField(
        'First Name of User', blank=True, max_length=20)
    last_name = models.CharField(
        'Last Name of User', blank=True, max_length=20)
    associated_identity = models.OneToOneField(
        'id_identities.VdxIdentity',
        on_delete=models.SET_NULL, null=True,
        help_text="Identity linked to user (determines 'my access')"
    )

    class Meta:
        permissions = (
            ("auth_admin", "User can alter all auth"),
        )
