from django.urls import path
from django.conf.urls import include
from myapp2 import views
urlpatterns=[
    path('about/',views.about),
]