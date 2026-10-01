from django.http import HttpResponse
from django.shortcuts import render
from django.template import loader


def home(request):
    template = loader.get_template('testpaper.html')
    res=template.render()
    return HttpResponse(res)



