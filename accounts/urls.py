from django.conf.urls import url
from django.contrib.auth import views as auth_views

from .views import \
(
RegistrationAPIView,
LoginAPIView,
UserRetrieveUpdateAPIView,
ProfileRetrieveAPIView,
)
app_name='accounts'

urlpatterns = [
    url(r'^register/?$', RegistrationAPIView.as_view()),
    url(r'^login/?$', LoginAPIView.as_view()),
    url(r'^profiles/(?P<username>\w+)/?$', UserRetrieveUpdateAPIView.as_view()),
     url(r'^get_profile/(?P<username>\w+)/?$', ProfileRetrieveAPIView.as_view()),
]
 
    