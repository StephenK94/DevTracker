
from django.urls import path
from . import views


urlpatterns = [
    path('search/', views.search_repositories, name='repository_search'),

    # Save a selected GitHub repository
    path(
        'save/<str:owner>/<str:repo>/',
        views.save_repository,
        name='save_repository'
    ),

    # Remove a saved repository
    path(
        'remove/<int:pk>/',
        views.remove_repository,
        name='remove_repository'
    ),
]
