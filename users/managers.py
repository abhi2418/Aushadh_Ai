from django.contrib.auth.base_user import BaseUserManager
from django.utils.translation import gettext_lazy as _


class CustomUserManager(BaseUserManager):
    """
    is_admin field to allow access to the admin app 
    """
    def create_user(self, username, password, **extra_fields):
        if not username:
            raise ValueError(_("The username must be set"))
        if not password:
            raise ValueError(_("The password must be set"))
        #username = self.normalize_email(username)

        user = self.model(username=username, **extra_fields)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, username, password, **extra_fields):
        extra_fields.setdefault('is_active', True)
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('role', 1)


        if extra_fields.get('role') != 1:
            raise ValueError('Superuser must have role of Global Admin')
        return self.create_user(username, password, **extra_fields)