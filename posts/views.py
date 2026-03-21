from django.views.generic import ListView, DetailView
from django.shortcuts import render
from .models import Post

class PostListView(ListView):
    model = Post
    template_name = "posts/post_list.html"
    paginate_by = 6

    def get_queryset(self):
        return Post.objects.filter(published=True).order_by("-created")

class PostDetailView(DetailView):
    model = Post
    template_name = "posts/post_detail.html"
    slug_field = "slug"
    slug_url_kwarg = "slug"

def about_view(request):
    return render(request, "pages/about.html")

def contact_view(request):
    return render(request, "pages/contact.html")

def social_view(request):
    from django.conf import settings
    links = getattr(settings, "SOCIAL_LINKS", {})
    return render(request, "pages/social.html", {"links": links})
