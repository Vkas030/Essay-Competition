from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from .forms import LoginForm

def user_login(request):
    form = LoginForm()

    if request.method == "POST":
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']

            user = authenticate(request, username=username, password=password)

            if user:
                login(request, user)
                return redirect('tasks:submit_task')   # redirect where you want
            else:
                return render(request, "login.html", {
                    "form": form,
                    "error": "Invalid username or password"
                })

    return render(request, "login.html", {"form": form})

def logout_view(request):
    logout(request)
    return redirect('home')
    