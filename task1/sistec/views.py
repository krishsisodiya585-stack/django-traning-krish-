from django.shortcuts import render
from django.http import HttpResponse



# Create your views here.

def about_sistec(request):
    s="<h1>Welcome to the  sistec </h1>"
    return HttpResponse(s)