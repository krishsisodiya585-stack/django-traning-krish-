from django.shortcuts import render
from django.http import HttpResponse

# Create your views here.
def home(request):
    s="<h1>Welcome to the aids </h1>"
    return HttpResponse(s)