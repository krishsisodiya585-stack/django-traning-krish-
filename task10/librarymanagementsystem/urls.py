from django.urls import path

from . import views


urlpatterns = [
    path('', views.home, name='home'),
    path('signup/', views.signup_view, name='signup'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('issue/', views.issue_book, name='issue_book'),
    path('issue/<int:issue_id>/success/', views.issue_success, name='issue_success'),
    path('books/', views.book_list, name='book_list'),
]