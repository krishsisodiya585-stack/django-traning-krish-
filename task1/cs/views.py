from django.shortcuts import render
from django.http import HttpResponse

# Create your views here.
def about_cs(request):
    s="<h1>Welcome to the cs </h1>"
    return HttpResponse(s)