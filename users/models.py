from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from uuid import uuid4
# Create your models here.


class SemicolonUserModelManager(BaseUserManager):

    def create_user(self, username, email, password=None):
        """
        Creates a custom user with give fields
        """

        user = self.model(
            username=username,
            email=self.normalize_email(email),
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password, username=None):
        user = self.create_user(
            email=email,
            password=password,
            username=username
        )
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user


class SemicolonUserModel(AbstractBaseUser, PermissionsMixin):
    userId   =models.CharField(max_length=32, default=uuid4, primary_key=True, editable=False )
    username =models.CharField(max_length=32, unique=True, null=True, blank=True)
    email    =models.EmailField(max_length = 100, unique =True, null=False, blank=False)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []
    active = models.BooleanField(default = True)
    is_staff = models.BooleanField(default= False)
    is_superuser = models.BooleanField(default= False)
    created_on = models.DateTimeField(auto_now_add = True, blank =True, null= True)
    objects = SemicolonUserModelManager()
    class Meta:
        verbose_name = "Semicolon User"
