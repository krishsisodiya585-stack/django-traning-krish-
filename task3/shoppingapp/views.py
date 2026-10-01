from django.shortcuts import render
from django.http import HttpResponse
from django.template import loader


def shopping(request):
    return render(request, 'shopping.html')