from django.db import models
import datetime
from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
    Permission,
    Group,
)
from mongoengine import Document, fields,ValidationError


class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("The Email field must be set")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self.create_user(email, password, **extra_fields)


class CustomUser(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    phone = models.CharField(max_length=15)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_verified = models.BooleanField(default=False)
    is_blocked = models.BooleanField(default=False)
    profile_image=models.ImageField(upload_to="profile",null=True)

    # Change the related_name to avoid clash
    groups = models.ManyToManyField(Group, blank=True, related_name="custom_users")
    user_permissions = models.ManyToManyField(
        Permission,
        blank=True,
        help_text="Specific permissions for this user.",
        related_name="custom_users",
    )

    objects = CustomUserManager()

    USERNAME_FIELD = "email"
    # REQUIRED_FIELDS = ["first_name", "last_name", "phone",]

    # def __str__(self):
    #     return self.email


class Address(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    house_name = models.CharField(max_length=255)
    street = models.CharField(max_length=255)
    place = models.CharField(max_length=100)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    country = models.CharField(max_length=100)
    postal_code = models.CharField(max_length=20)





class UnverifiedEmails(Document):
    user_email = fields.StringField(required=False,unique=True)
    user_phone = fields.StringField(required=False)
    created_at = fields.DateTimeField(default=datetime.datetime.utcnow)
    otp=fields.IntField(required=False)
    is_verified=fields.BooleanField(default=False)
    meta = {
        'indexes': [
            {'fields': ['created_at'], 'expireAfterSeconds': 360}  # TTL index to expire documents after 6 minutes (360 seconds)
        ]
    }

    def clean(self):
        if not self.user_email and not self.user_phone:
            raise ValidationError("At least one of user_email or user_phone must be provided.")
        super().clean() 