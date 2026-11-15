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

    # Get the available programming languages
    languages = saved_repositories.exclude(language='').values_list(
        'language', flat=True
    ).distinct().order_by('language')

    # Filter repositories by the selected language
    selected_language = request.GET.get('language', '')

    if selected_language:
        saved_repositories = saved_repositories.filter(
            language=selected_language
        )

    return render(request, 'accounts/dashboard.html', {
        'saved_repositories': saved_repositories,
        'languages': languages,
        'selected_language': selected_language
    })

