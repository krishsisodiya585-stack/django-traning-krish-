from django.shortcuts import render


def home(request):
    return render(request, 'home.html')


def sistec(request):
    return render(request, 'sistec.html')


def lnct(request):
    return render(request, 'lnct.html')


def oist(request):
    return render(request, 'oist.html')
