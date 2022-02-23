from django.db import models

# Create your models here.
import uuid

from django.db import models
from django.contrib.auth.models import PermissionsMixin
from django.contrib.auth.base_user import AbstractBaseUser
from django.utils import timezone

from .managers import CustomUserManager

# Create your models here.
class User(AbstractBaseUser, PermissionsMixin):

    # These fields tie to the roles!
    ADMIN = 1
    SUPERVISOR = 2
    OPERATOR = 3

    ROLE_CHOICES = (
        (ADMIN, 'Admin'),
        (SUPERVISOR, 'Supervisor'),
        (OPERATOR, 'Operator')
    )

    class Meta:
        verbose_name = 'user'
        verbose_name_plural = 'users'

    #email = models.EmailField(unique=True)
    username = models.CharField(max_length=30,unique=True)
    role = models.PositiveSmallIntegerField(choices=ROLE_CHOICES, blank=True, null=True, default=3)
    date_joined = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    is_deleted = models.BooleanField(default=False)
    created_date = models.DateTimeField(default=timezone.now)
    created_by = models.CharField(max_length=30)
    modified_by = models.CharField(max_length=30)
    is_staff =  models.BooleanField(default=False)

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = []

    objects = CustomUserManager()

    def __str__(self):
        return self.username