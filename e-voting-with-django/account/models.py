from django.contrib.auth.models import AbstractUser, UserManager
from django.db import models
from django.contrib.auth.hashers import make_password
from django.db.models.signals import post_save
from django.dispatch import receiver
import json

# Create your models here.

class StrKeyVal(models.Model):
    # container = models.ForeignKey(Dicty,on_delete=models.CASCADE, db_index=True)
    dkey       = models.CharField(db_index=True, max_length=200)
    dvalue     = models.TextField(db_index=True,max_length=12000, default="")
    def set_dvalue(self,x):
        self.dvalue = json.dumps(x)
    
    def get_dvalue(self):
        if self.dvalue is "":
            return []
        return json.loads(self.dvalue)

class CustomUserManager(UserManager):
    def _create_user(self, email, password, **extra_fields):
        email = self.normalize_email(email)
        user = CustomUser(email=email, **extra_fields)
        user.password = make_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("user_type", 1)
        extra_fields.setdefault("last_name", "System")
        extra_fields.setdefault("first_name", "Administrator")
        extra_fields.setdefault("branch", "ARCH")

        assert extra_fields["is_staff"]
        assert extra_fields["is_superuser"]
        return self._create_user(email, password, **extra_fields)


class CustomUser(AbstractUser):
    USER_TYPE = ((1, "Admin"), (2, "Voter"))
    username = None  # Removed username, using email instead
    email = models.EmailField(unique=True)
    user_type = models.CharField(default=2, choices=USER_TYPE, max_length=1)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []
    objects = CustomUserManager()
    branch = models.CharField(max_length=100, default = 'arch')
    pos_key_dict = models.ManyToManyField(StrKeyVal)
    otp_reset_pass = models.CharField(max_length=20, null=True)
   
    

    def __str__(self):
        return self.last_name + " " + self.first_name
