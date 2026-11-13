
import requests
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST
from .models import SavedRepository


def search_repositories(request):
    # Get the search term entered by the user
    query = request.GET.get('q', '').strip()
    repositories = []
    error = None

    if query:
        url = "https://api.github.com/search/repositories"

        # Set the GitHub API search parameters
        params = {
            "q": query,
            "per_page": 5
        }

        try:
            # Request repository data from GitHub
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()

            data = response.json()
            repositories = data.get("items", [])

        except requests.RequestException:
            # Display a message if the API request fails
            error = "Unable to retrieve repositories. Please try again."

    return render(request, "repositories/search.html", {
        "repositories": repositories,
        "query": query,
        "error": error
    })


@login_required
@require_POST
def save_repository(request, owner, repo):
    # Retrieve the repository details directly from GitHub
    url = f"https://api.github.com/repos/{owner}/{repo}"

    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()

        # Save the repository without creating duplicates
        saved_repo, created = SavedRepository.objects.get_or_create(
            user=request.user,
            github_id=data["id"],
            defaults={
                "name": data["full_name"],
                "description": data.get("description") or "",
                "url": data["html_url"],
                "language": data.get("language") or "",
            }
        )

        if created:
            messages.success(request, "Repository saved successfully.")
        else:
            messages.info(request, "You have already saved this repository.")

    except requests.RequestException:
        messages.error(request, "Unable to save repository. Please try again.")

    return redirect('repository_search')


@login_required
@require_POST
def remove_repository(request, pk):
    # Only allow users to remove their own repositories
    repository = get_object_or_404(
        SavedRepository,
        pk=pk,
        user=request.user
    )

    repository.delete()

    messages.success(request, "Repository removed successfully.")

    return redirect('dashboard')
