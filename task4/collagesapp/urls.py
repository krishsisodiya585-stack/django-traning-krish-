from django.urls import path
from . import views


urlpatterns = [

    path('', views.home, name='home'),

    path('sistec/', views.sistec, name='sistec'),

    path('lnct/', views.lnct, name='lnct'),

    path('oist/', views.oist, name='oist'),

]