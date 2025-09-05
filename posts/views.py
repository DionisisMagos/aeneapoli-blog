from django.views.generic import ListView, DetailView
from django.shortcuts import render
from .models import Post

class PostListView(ListView):
    model = Post
    paginate_by = 6
    template_name = 'posts/post_list.html'
    queryset = Post.objects.filter(published=True).order_by('-created')

class PostDetailView(DetailView):
    model = Post
    template_name = 'posts/post_detail.html'

def about_view(request):
    return render(request, 'pages/about.html')

def contact_view(request):
    return render(request, 'pages/contact.html')

def social_view(request):
    from django.conf import settings
    links = getattr(settings, 'SOCIAL_LINKS', {})
    return render(request, 'pages/social.html', {'links': links})
