from myapp1 import views
from django.http import HttpResponse
from django.template import loader

# Create your views here.
def home(request):
    template = loader.get_template('home.html')
    res=template.render()
    return HttpResponse(res)


def about(request):
    template = loader.get_template('about.html')
    res=template.render()
    return HttpResponse(res)

def testpaper(request):
    template = loader.get_template('testpaper.html')
    res=template.render()
    return HttpResponse(res)
