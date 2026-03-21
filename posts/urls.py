from django.urls import path
from .views import PostListView, PostDetailView, about_view, contact_view, social_view

app_name = "posts"

urlpatterns = [
    path("", PostListView.as_view(), name="list"),
    path("about/", about_view, name="about"),
    path("contact/", contact_view, name="contact"),
    path("social/", social_view, name="social"),
    path("<slug:slug>/", PostDetailView.as_view(), name="detail"),
]
