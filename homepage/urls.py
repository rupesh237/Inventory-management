from django.urls import path
from . import views

urlpatterns = [
    path('', views.HomeView.as_view(), name='home'),
    path('about/', views.AboutView.as_view(), name='about'),

    path('branches/', views.BranchListView.as_view(), name="branch-list"),
    path('branches/new', views.BranchCreateView.as_view(), name="new-branch"),
    path('branches/<pk>/edit', views.BranchUpdateView.as_view(), name="edit-branch"),
    path('branches/<pk>/delete', views.BranchDeleteView.as_view(), name="delete-branch"),
    path('branches/<str:name>/', views.BranchView.as_view(), name='branch_profile'),

    path('branches/<int:branch_id>/add_user/', views.UserCreateView.as_view(), name='add-user'),
    path('branches/<int:branch_id>/edit_user/<int:pk>/', views.UserUpdateView.as_view(), name='edit-user'),
    path('delete_user/<int:pk>/', views.UserDeleteView.as_view(), name='delete-user'),
]