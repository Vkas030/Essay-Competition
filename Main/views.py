from django.shortcuts import render
def home(request):
    return render(request, 'home.html')
def score(request):
    return render(request, 'score.html')

# Create your views here.
