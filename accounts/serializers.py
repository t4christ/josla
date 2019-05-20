from rest_framework import serializers
from django.contrib.auth import authenticate
from .models import User,Profile
from django.core.files.base import ContentFile
import base64
from rest_framework_friendly_errors.mixins import FriendlyErrorMessagesMixin


class Base64ImageField(serializers.ImageField):
    def to_internal_value(self, data):
        from django.core.files.base import ContentFile
        import base64
        import six
        import uuid
        print("ininternal")
        # Check if this is a base64 string
        if isinstance(data, six.string_types):
            # Check if the base64 string is in the "data:" format
            print("ininstance")
            if 'data:' in data and ';base64,' in data:
                # Break out the header from the base64 content
                header, data = data.split(';base64,')

            # Try to decode the file. Return validation error if it fails.
            try:
                decoded_file = base64.b64decode(data)
            except TypeError:
                self.fail('invalid_image')

            # Generate file name:
            file_name = str(uuid.uuid4())[:12] # 12 characters are more than enough.
            # Get the file name extension:
            file_extension = self.get_file_extension(file_name, decoded_file)

            complete_file_name = "%s.%s" % (file_name, file_extension, )

            data = ContentFile(decoded_file, name=complete_file_name)

        return super(Base64ImageField, self).to_internal_value(data)

    def get_file_extension(self, file_name, decoded_file):
        import imghdr

        extension = imghdr.what(file_name, decoded_file)
        extension = "jpg" or "jpeg" if extension == "png" else extension

        return extension


class RegistrationSerializer(serializers.ModelSerializer
):
    """Serializers registration requests and creates a new user."""

    # Ensure passwords are at least 8 characters long, no longer than 128
    # characters, and can not be read by the client.
    password = serializers.CharField(
        max_length=128,
        min_length=8,
        write_only=True
    )
  

    # The client should not be able to send a token along with a registration
    # request. Making `token` read-only handles that for us.
    token = serializers.CharField(max_length=255, read_only=True)
    class Meta:
        model = User
        # List all of the fields that could possibly be included in a request
        # or response, including fields specified explicitly above.
        fields = ['email', 'username','first_name','last_name','phone_number','password','token']

    def create(self, validated_data):

        return User.objects.register_user(**validated_data)

class LoginSerializer(serializers.Serializer):
    email = serializers.CharField(max_length=255,read_only=True)
    username = serializers.CharField(max_length=255)
    password = serializers.CharField(max_length=128, write_only=True)
    token = serializers.CharField(max_length=255, read_only=True)

    def validate(self, data):
   
        username = data.get('username', None)
        password = data.get('password', None)

        # Raise an exception if an
        # username is not provided.
        if username is None:
            raise serializers.ValidationError(
                'An username is required to log in.'
            )

        # Raise an exception if a
        # password is not provided.
        if password is None:
            raise serializers.ValidationError(
                'A password is required to log in.'
            )


        user = authenticate(username=username, password=password)

        # If no user was found matching this email/password combination then
        # `authenticate` will return `None`. Raise an exception in this case.
        if user is None:
            raise serializers.ValidationError(
                'A user with this username and password was not found.'
            )

        if not user.is_active:
            raise serializers.ValidationError(
                'This user has been deactivated.'
            )
        print("User Token",user.token)
        # The `validate` method should return a dictionary of validated data.
        # This is the data that is passed to the `create` and `update` methods
        # that we will see later on.
        return {
            'email': user.email,
            'username': user.username,
            'token': user.token
        }


class ProfileSerializer(serializers.HyperlinkedModelSerializer):
    # user = serializers.CharField(source='user.username')
    user = serializers.SerializerMethodField('user_set')
    bio = serializers.CharField(allow_blank=True, required=False)
    photo = Base64ImageField(allow_null=True,max_length=None,use_url=True)


    class Meta:
        model = Profile
        fields = ('user', 'bio', 'photo',)
        read_only_fields = ('user',)

    def user_set(self, profile):
        queryset = User.objects.get(profile=profile)
        serializer = UserSerializer(instance=queryset)
        return serializer.data







class UserSerializer(serializers.ModelSerializer):
    """Handles serialization and deserialization of User objects."""


    password = serializers.CharField(
        max_length=128,
        min_length=8,
        write_only=True
    )


    profile = ProfileSerializer(write_only=True)

    # We want to get the `bio` and `image` fields from the related Profile
    # model.
    bio = serializers.CharField(source='profile.bio', read_only=True)
    # photo = Base64ImageField(source='profile.photo',max_length=None, use_url=True, read_only=True)
    # photo = serializers.CharField(source='profile.photo', max_length=100000,read_only=True)

    class Meta:
        model = User
        fields = ('email', 'username', 'first_name','last_name','phone_number','password','profile','bio',)

        read_only_fields = ('token',)


    def update(self, instance, validated_data):
        """Performs an update on a User."""

        password = validated_data.pop('password', None)
        profile_data = validated_data.pop('profile', {})

        print("Pop profile",profile_data)
        print("Pop password",password)

        for (key, value) in validated_data.items():
            # For the keys remaining in `validated_data`, we will set them on
            # the current `User` instance one at a time.
            print("May Instance",instance,key,value)
            print("May Validated Data",validated_data.items())
            setattr(instance, key, value)

        if password is not None:
            # `.set_password()`  handles all
            # of the security stuff that we shouldn't be concerned with.
            instance.set_password(password)

        # After everything has been updated we must explicitly save
        # the model. It's worth pointing out that `.set_password()` does not
        # save the model.
        instance.save()

        for (key, value) in profile_data.items():
        # We're doing the same thing as above, but this time we're making
        # changes to the Profile model.
            print("May Validated Data",profile_data.items())
            setattr(instance.profile, key, value)

            # Save the profile just like we saved the user.
            instance.profile.save()

        return instance

