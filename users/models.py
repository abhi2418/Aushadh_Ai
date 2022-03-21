from django.db import models
import pyotp
# Create your models here.
import uuid

from django.db import models
from django.contrib.auth.models import PermissionsMixin
from django.contrib.auth.base_user import AbstractBaseUser
from django.utils import timezone
#from phonenumber_field.modelfields import PhoneNumberField
from .managers import CustomUserManager
from django.core.validators import RegexValidator
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


    username = models.CharField(max_length=30,unique=True)
    role = models.PositiveSmallIntegerField(choices=ROLE_CHOICES, blank=True, null=True, default=3)
    date_joined = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    is_deleted = models.BooleanField(default=False)
    created_date = models.DateTimeField(default=timezone.now)
    created_by = models.CharField(max_length=30)
    modified_by = models.CharField(max_length=30)
    is_staff =  models.BooleanField(default=False)
    key = models.CharField(max_length=100, unique=True, blank=True)
    verified = models.BooleanField(default=False)
    phone_regex = RegexValidator(regex=r'^\+?1?\d{9,15}$', message="Phone number must be entered in the format: '+91'. Up to 13 digits allowed.")
    phone_number = models.CharField(validators=[phone_regex], max_length=17, blank=True) # validators should be a list
    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = []

    objects = CustomUserManager()

    def __str__(self):
        return self.username
    
    def authenticate(self, otp):
        """ This method authenticates the given otp handles verification of the otp  """
        provided_otp = 0
        try:
            provided_otp = int(otp)
        except:
            return False
        #Here we are using Time Based OTP. The interval is 300 seconds.
        #otp must be provided within this interval or it's invalid
        t = pyotp.TOTP(self.key, interval=300)
        return t.verify(provided_otp)

