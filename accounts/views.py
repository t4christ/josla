from rest_framework import status
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import AllowAny,IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.generics import RetrieveUpdateAPIView,RetrieveAPIView,ListAPIView
from .exceptions import ProfileDoesNotExist
from .models import Profile,User
from .serializers import (RegistrationSerializer,LoginSerializer,UserSerializer,ProfileSerializer)


class RegistrationAPIView(APIView):
    # Allow any user (authenticated or not) to hit this endpoint.
    permission_classes = (AllowAny,)
    serializer_class = RegistrationSerializer
    def pre_save(self, obj):
        obj.photo = self.request.FILES.get('file')
    def post(self, request):
        password = request.data.get('password', {})
        email = request.data.get('email', {})
        confirm_pass=request.data.get('confirm_password',{})
        print(password,confirm_pass)
        if password == confirm_pass:
            serializer = self.serializer_class(data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save(email=email)

            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return  Response('Passwords must match')

class LoginAPIView(APIView):
    permission_classes = (AllowAny,)
    # renderer_classes = (UserJSONRenderer,)
    serializer_class = LoginSerializer
  

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        return Response(serializer.data, status=status.HTTP_200_OK)


class UserRetrieveUpdateAPIView(RetrieveUpdateAPIView):
    permission_classes = (IsAuthenticated,)
    # authentication_classes = (TokenAuthentication,) 
    serializer_class = UserSerializer

    def retrieve(self, request, *args, **kwargs):
        # There is nothing to validate or save here. Instead, we just want the
        # serializer to handle turning our `User` object into something that
        # can be JSONified and sent to the client.
        serializer = self.serializer_class(request.user)

        return Response(serializer.data, status=status.HTTP_200_OK)

    def update(self, request, *args, **kwargs):

        serializer_data = {
            'username': request.data.get('username', request.user.username),
            'phone_number': request.data.get('phone_number', request.user.phone_number),
            'email': request.data.get('email', request.user.email),
            'profile': {
                'bio': request.data.get('bio', request.user.profile.bio),
                'photo': request.data.get('photo', request.user.profile.photo)
            }
        }
        serializer = self.serializer_class(
            request.user, data=serializer_data, partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data, status=status.HTTP_200_OK)


class ProfileRetrieveAPIView(RetrieveAPIView):
    permission_classes = (IsAuthenticated,)
    # renderer_classes = (ProfileJSONRenderer,)
    serializer_class = ProfileSerializer

    def retrieve(self, request, username, *args, **kwargs):
        # Try to retrieve the requested profile and throw an exception if the
        # profile could not be found.
        try:
            # We use the `select_related` method to avoid making unnecessary
            # database calls.
            profile = Profile.objects.select_related('user').get(
                user__username=username
            )
        except Profile.DoesNotExist:
            raise

        serializer = self.serializer_class(profile)

        return Response(serializer.data, status=status.HTTP_200_OK)


