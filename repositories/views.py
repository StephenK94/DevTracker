
import requests
from django.shortcuts import render


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

