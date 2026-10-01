from django.http import HttpResponse
from django.shortcuts import render

# Create your views here.
def about_sistec(request):
    s="<h1>Welcome to the sistec </h1>"
    return HttpResponse(s)