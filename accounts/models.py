
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _
from django.dispatch import receiver
from django.db.models.signals import post_save


USER_TYPE = (
    ("Talent", "Talent"),
    ("Hunter", "Hunter"),
)
class User(AbstractUser):
    is_email_verified = models.BooleanField(default=False)
    user_type = models.CharField(max_length=15, choices=USER_TYPE, null=True)

    def __str__(self):
        return self.email


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    avatar = models.ImageField(default="profile1.png", null=True, blank=True)
    full_name = models.CharField(max_length=150, null=True, blank=True)
    bio = models.TextField(_(
        'bio'), max_length=500, null=True, blank=True)
    
    def __str__(self):
        return self.user.username

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)