from django.urls import path
from app1 import views
urlpatterns = [
    path('about_sistec/',views.about_sistec),
    path('about_cs/',views.about_cs),
]