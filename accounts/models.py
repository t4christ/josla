import jwt

from datetime import datetime, timedelta

from django.conf import settings
from django.contrib.auth.models import (
    AbstractBaseUser, BaseUserManager, PermissionsMixin
)
from django.db import models


class TimestampedModel(models.Model):
    # A timestamp representing when this object was created.
    created_at = models.DateTimeField(auto_now_add=True)

    # A timestamp reprensenting when this object was last updated.
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True




class UserManager(BaseUserManager):
    """
    Django requires that custom users define their own Manager class. By
    inheriting from `BaseUserManager`, we get a lot of the same code used by
    Django to create a `User`. 

    All we have to do is override the `create_user` function which we will use
    to create `User` objects.
    """

    def create_user(self, username, email, password=None):
        """Create and return a `User` with an email, username and password."""
        if username is None:
            raise TypeError('Users must have a username.')

        if email is None:
            raise TypeError('Users must have an email address.')

        user = self.model(username=username, email=self.normalize_email(email))
        user.set_password(password)
        user.save()

        return user

    def create_superuser(self, username, email, password):
        """
        Create and return a `User` with superuser (admin) permissions.
        """
        if password is None:
            raise TypeError('Superusers must have a password.')

        user = self.create_user(username, email, password)
        user.is_superuser = True
        user.is_staff = True
        user.save()

        return user

    def register_user(self, username, email,phone_number,first_name,last_name,password=None,confirm_password=None):
        """Create and return a `User` with an email, username and password."""
        if username is None:
            raise TypeError('Users must have a username.')

        if email is None:
            raise TypeError('Users must have an email address.')

        if first_name is None:
            raise TypeError('Users must have a first_name.')

        if last_name is None:
            raise TypeError('Users must have a last_name.')

        if phone_number is None:
            raise TypeError('Users must have a phone_number.')
        
        # if confirm_password != password:
        #     raise TypeError("Passwords must match")



        user = self.model(username=username, first_name=first_name,last_name=last_name,phone_number=phone_number, email=self.normalize_email(email))
        user.set_password(password)
        user.save()

        return user



class User(AbstractBaseUser, PermissionsMixin,TimestampedModel):
    # Each `User` needs a human-readable unique identifier that we can use to
    # represent the `User` in the UI. We want to index this column in the
    # database to improve lookup performance.
    username = models.CharField(db_index=True, max_length=255, unique=True)

    email = models.EmailField(db_index=True, unique=True)

    first_name = models.CharField(max_length=200,default="")

    phone_number = models.CharField(max_length=11,default="",unique=True)

    last_name = models.CharField(max_length=200,default="")

    is_active = models.BooleanField(default=True)

  
    is_staff = models.BooleanField(default=False)

    
    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email']

    # Tells Django that the UserManager class defined above should manage
    # objects of this type.
    objects = UserManager()

    def __str__(self):
        """
        Returns a string representation of this `User`.

        This string is used when a `User` is printed in the console.
        """
        return self.username

    @property
    def token(self):
        """
        Allows us to get a user's token by calling `user.token` instead of
        `user.generate_jwt_token().

        The `@property` decorator above makes this possible. `token` is called
        a "dynamic property".
        """
        return self._generate_jwt_token()

    def get_short_name(self):
        """
        This method is required by Django for things like handling emails.
        Typically this would be the user's first and last name. Since we do
        not store the user's real name, we return their username instead.
        """
        return self.username

    def get_full_name(self):
        """
        This method is required by Django for things like handling emails.
        Typically, this would be the user's first name. Since we do not store
        the user's real name, we return their username instead.
        """
        return "{} {}".format(self.first_name,self.last_name)

    def _generate_jwt_token(self):
        """
        Generates a JSON Web Token that stores this user's ID and has an expiry
        date set to 60 days into the future.
        """
        dt = datetime.now() + timedelta(days=60)

        token = jwt.encode({
            'id': self.pk,
            'exp': int(dt.strftime('%s'))
        }, settings.SECRET_KEY, algorithm='HS256')

        return token.decode('utf-8')



class Profile(TimestampedModel):

    user = models.OneToOneField(
        'accounts.User', on_delete=models.CASCADE
    )
  
    bio = models.TextField(blank=True)

    photo = models.ImageField(upload_to=settings.MEDIA_URL, max_length=100000, null=True, blank=True,default="https://static.productionready.io/images/smiley-cyrus.jpg")



    def __str__(self):
        return self.user.username