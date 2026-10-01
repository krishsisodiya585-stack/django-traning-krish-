from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('sign_up/', views.sign_up, name='sign_up'),
    path('save_user/', views.save_user, name='save_user'),
    path('login/', views.login, name='login'),
    path('login_vel/', views.login_vel, name='login_vel'),
    path('student-register/', views.student_register, name='student_register'),
    path('logout/', views.logout, name='logout'),
]