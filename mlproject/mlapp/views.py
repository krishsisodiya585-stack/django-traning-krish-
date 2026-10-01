from django.shortcuts import render
from django.http import HttpResponse
from django.template import loader
import joblib

# Create your views here.
def home(request):
    return render(request, 'mlapp/home.html')


def result(request):
    scaler = joblib.load('scalermodel.pkl')
    mlmodel = joblib.load('mlmodel.pkl')
    values = []
    values.append(request.GET['RI'])
    values.append(request.GET['Na'])
    values.append(request.GET['Mg'])
    values.append(request.GET['Al'])
    values.append(request.GET['Si'])
    values.append(request.GET['K'])
    values.append(request.GET['Ca'])
    values.append(request.GET['Ba'])
    values.append(request.GET['Fe'])

    scaled_input = scaler.transform([values])
    ans = mlmodel.predict(scaled_input)[0]

    return render(request, 'mlapp/result1.html', {'ans': ans, 'list': values})