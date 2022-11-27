from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager

class UserManager(BaseUserManager):
    """Overriding the default django user model"""
    def create_user(self, email, first_name, last_name, department, password=None):
        """Django cli function creating/registering new users"""
        if not email:
            raise ValueError("Email Must Be Supplied !!!")
        email = self.normalize_email(email)
        user = self.model(email=email, first_name=first_name, last_name=last_name, department=department)
        user.set_password(password)
        user.save()
        return user 

    def create_superuser(self, email,first_name, last_name, department, password):
        """Django cli function creating/registering superusers"""
        user = self.create_user(email, first_name, last_name, department, password)
        user.is_staff = True 
        user.is_superuser = True
        user.save()
        return user 


class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    department = models.CharField(max_length=100)
    is_verified = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateField(auto_now_add=True)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name', 'department']

    @property
    def full_name(self):
        return "".format(self.first_name, self.last_name)


    class Meta:
        ordering = ['-date_joined']