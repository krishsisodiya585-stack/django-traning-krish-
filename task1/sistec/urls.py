from django.urls import path
from sistec import views
urlpatterns = [
    path('about_sistec/',views.about_sistec,name='about_sistec'),
]