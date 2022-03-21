from django.db.models.signals import pre_save
from django.dispatch import receiver
from .models import User
import pyotp


"""
we first check if the user already have 
a key before generating one for them. 
It’s important to check this because pre_save 
is called every time a user is added or updated.

"""

def generate_key():
    """ User otp key generator """
    key = pyotp.random_base32()
    if is_unique(key):
        return key
    generate_key()

def is_unique(key):
    """
    checks for uniqueness. 
    If we can’t find a user with the generated key, then the key is unique.

    """
    try:
        User.objects.get(key=key)
    except User.DoesNotExist:
        return True
    return False

@receiver(pre_save, sender=User)
def create_key(sender, instance, **kwargs):
    """This creates the key for users that don't have keys"""
    if not instance.key:
        instance.key = generate_key()
