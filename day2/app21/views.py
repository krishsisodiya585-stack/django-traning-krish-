from django.http import HttpResponse
from django.shortcuts import render

# Create your views here.
def home(request):
    s="<h1>Welcome to the app1 </h1>"
    return HttpResponse(s)