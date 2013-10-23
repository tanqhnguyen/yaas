from django.shortcuts import render, redirect
from forms import RegistrationForm
from django.contrib.auth import authenticate, login

def register(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(True)
            user = authenticate(username=request.POST['username'], password=request.POST['password1'])
            login(request, user)
            return redirect('/')
    else:
        form = RegistrationForm()

    context = {'form': form}
    return render(request, 'authentication/register.html', context)