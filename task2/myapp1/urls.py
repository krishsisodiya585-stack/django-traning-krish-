from django.shortcuts import render
from django.conf.urls import path
from myapp1 import views

urlpatterns = [
    path('home/', views.home),
]
