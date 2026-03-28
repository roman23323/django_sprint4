from django.shortcuts import render
from django.shortcuts import render, get_object_or_404
from django.utils import timezone
from .models import Post, Category


def index(request):
    posts = Post.objects.select_related(
        'author', 'category', 'location').filter(
        is_published=True,
        pub_date__lte=timezone.now(),
        category__is_published=True
    )[:5]
    return render(request, 'blog/index.html', {'post_list': posts})


def post_detail(request, post_id):
    post = get_object_or_404(
        Post.objects.select_related('author', 'category', 'location'),
        pk=post_id,
        is_published=True,
        pub_date__lte=timezone.now(),
        category__is_published=True
    )
    return render(request, 'blog/detail.html', {'post': post})


def category_posts(request, category_slug):
    category = get_object_or_404(
        Category,
        slug=category_slug,
        is_published=True
    )
    posts = Post.objects.select_related('author', 'location').filter(
        category=category,
        is_published=True,
        pub_date__lte=timezone.now()
    )
    return render(request, 'blog/category.html', {
        'category': category, 'post_list': posts})
