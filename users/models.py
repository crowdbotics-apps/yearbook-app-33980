from django.contrib.auth.models import AbstractUser
from django.db import models
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _


class User(AbstractUser):
    # WARNING!
    """
    Some officially supported features of Crowdbotics Dashboard depend on the initial
    state of this User model (Such as the creation of superusers using the CLI
    or password reset in the dashboard). Changing, extending, or modifying this model
    may lead to unexpected bugs and or behaviors in the automated flows provided
    by Crowdbotics. Change it at your own risk.


    This model represents the User instance of the system, login system and
    everything that relates with an `User` is represented by this model.
    """

    USER_TYPE_CHOICES = (
      (1, 'student'),
      (2, 'admin'),
      (3, 'superadmin'),
    )

    name = models.CharField(
        null=True,
        blank=True,
        max_length=255,
    )
    lname = models.CharField(
        max_length=256,
        null=True,
        blank=True,
    )
    dob = models.DateField(
        null=True,
        blank=True,
    )
    high_school = models.ForeignKey(
        'yearbook.HighSchool',
        null=True,
        blank=True,
        on_delete=models.CASCADE
    )
    address = models.TextField(
        null=True,
        blank=True,
    )
    zip_code = models.CharField(
        max_length=256,
        null=True,
        blank=True,
    )
    status = models.CharField(
        max_length=256,
        null=True,
        blank=True,
        default='pending'
    )
    photo = models.FileField(blank=True)

    role = models.PositiveSmallIntegerField(
        choices=USER_TYPE_CHOICES,
        default=1
    )
    stripe_id = models.CharField(max_length=50)
    
    def get_absolute_url(self):
        return reverse("users:detail", kwargs={"username": self.username})
