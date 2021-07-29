from django.urls import path

from users.views import SignupView, SigninView, KakaoSigninView, HostView

urlpatterns = [
     path('/signup', SignupView.as_view()),
     path('/signin', SigninView.as_view()),
     path('/kakao/signin', KakaoSigninView.as_view()),
     path('/host', HostView.as_view())
]