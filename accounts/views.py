from django.contrib.auth import login
from django.shortcuts import render, redirect
from repositories.models import SavedRepository

from .forms import RegisterForm


def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)

        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('dashboard')
    else:
        form = RegisterForm()

    return render(request, 'accounts/register.html', {'form': form})

from django.contrib.auth.decorators import login_required



@login_required
def dashboard(request):
    # Retrieve repositories belonging to the logged-in user
    saved_repositories = SavedRepository.objects.filter(
        user=request.user
    ).order_by('-saved_at')

    return render(request, 'accounts/dashboard.html', {
        'saved_repositories': saved_repositories
    })
