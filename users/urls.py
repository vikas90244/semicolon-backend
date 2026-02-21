from django.contrib import admin
from django.urls import path

from users.views import GoogleLoginView


urlpatterns =[
    path('google/', GoogleLoginView.as_view(), name="google"),
]
