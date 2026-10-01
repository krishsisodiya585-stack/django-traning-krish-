from django.shortcuts import render
from django.http import HttpResponse
from django.template import loader

# Create your views here.
def testpaper(request):
    que=" who developed python?"
    a="Guido van Rossum"
    b="Dennis Ritchie"
    c="Bjarne Stroustrup"
    d="James Gosling"
    context={
        'que': que,
        'a': a,
        'b': b,
        'c': c,
        'd': d
    }
    templates= loader.get_template('testpaper.html')
    res=templates.render(context,request)
    return HttpResponse(res)
def info(request):
    name="krish sisodiya"
    depatment="aids"
    age=21
    context={
        'name': name,
        'department': depatment,
        'age': age
    }
    template = loader.get_templates('info.html')
    res=template.render(context,request)
    return HttpResponse(res)
def sum(request):
    a=3
    b=5
    c=7
    d=9
    context={

    
        'a': a,
        'b': b,
        'c': c,
        'd': d
    }
    templates= loader.get_template('sum.html')
    res=templates.render(context,request)
    return HttpResponse(res)
def result(request):
   context={
       'name':"krish sisodiya",
        'marks': 90,
    }
   return render(request,'result.html',context)
def voting(request):
    age=21
    context={
        'age': age
    }
    return render(request,'voting.html',context)