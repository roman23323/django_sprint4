from django.http import Http404
from django.shortcuts import redirect, render
from django.shortcuts import render, get_object_or_404
from django.utils import timezone
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required
from django.db.models import Count

from .forms import EditProfileForm, CommentForm, CreatePostForm
from .models import Post, Category, User, Comment


def index(request):
    posts = Post.objects.select_related(
        'author', 'category', 'location'
    ).annotate(
        comment_count=Count('comments')
    ).filter(
        is_published=True,
        pub_date__lte=timezone.now(),
        category__is_published=True
    ).order_by(
        '-pub_date', '-id'
    )
    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'blog/index.html', {
        'page_obj': page_obj
        })


def post_detail(request, post_id):
    post = get_object_or_404(
        Post.objects.select_related('author', 'category', 'location'),
        pk=post_id
    )
    if not post.is_published \
        or not post.category.is_published \
        or post.pub_date > timezone.now():
        if not request.user.is_authenticated or request.user != post.author:
            raise Http404("Post not found")
    
    comments = Comment.objects.filter(
        post=post,
        created_at__lte=timezone.now(),
    )
    form = CommentForm(request.POST or None)
    return render(request, 'blog/detail.html', {'post': post, 'form': form, 'comments': comments})


def category_posts(request, category_slug):
    category = get_object_or_404(
        Category,
        slug=category_slug,
        is_published=True
    )
    posts = Post.objects.select_related('author', 'location'
    ).annotate(
        comment_count=Count('comments')
    ).filter(
        category=category,
        is_published=True,
        pub_date__lte=timezone.now()
    ).order_by(
        '-pub_date', '-id'
    )
    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'blog/category.html', {
        'category': category,
        'page_obj': page_obj
        })


def profile(request, username):
    user = get_object_or_404(User, username=username)
    if request.user.is_authenticated and request.user.username == username:
        posts = Post.objects.select_related(
            'author', 'category', 'location'
        ).annotate(
            comment_count=Count('comments')
        ).filter(
            author=user
        ).order_by(
            '-pub_date', '-id'
        )
    else:
        posts = Post.objects.select_related(
            'author', 'category', 'location'
        ).annotate(
            comment_count=Count('comments')
        ).filter(
            is_published=True,
            pub_date__lte=timezone.now(),
            category__is_published=True,
            author=user
        ).order_by(
            '-pub_date', '-id'
        )
    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'blog/profile.html', {
        'profile': user,
        'page_obj': page_obj
    })


@login_required
def edit_profile(request):
    instance = request.user
    form = EditProfileForm(request.POST or None, instance=instance)
    context = {'form':form}
    if form.is_valid():
        form.save()
    return render(request, 'blog/user.html', context)

@login_required
def add_comment(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    form = CommentForm(request.POST)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect('blog:post_detail', post_id=post_id)


@login_required
def edit_comment(request, post_id, comment_id):
    post = get_object_or_404(Post, pk=post_id)
    comment = get_object_or_404(Comment, pk=comment_id, post=post)
    if request.user != comment.author:
        return redirect ('blog:post_detail', post_id)
    form = CommentForm(instance=comment)
    if request.method == 'POST':
        form = CommentForm(request.POST, instance=comment)
        if form.is_valid():
            form.save()
            return redirect('blog:post_detail', post_id)
    else:
        form = CommentForm(instance=comment)
    context = {
        'form': form,
        'comment': comment,
        'post': post
    }
    return render(request, 'blog/comment.html', context)

@login_required
def delete_comment(request, post_id, comment_id):
    comment = get_object_or_404(
        Comment,
        pk=comment_id
    )
    if request.method == 'POST':
        if request.user == comment.author or request.user.is_staff:
            comment.delete()
        return redirect('blog:post_detail', post_id)
    return render(request, 'blog/comment.html')


@login_required
def create_post(request):
    form = CreatePostForm(
        request.POST or None,
        files=request.FILES or None
    )
    if form.is_valid():
        post = form.save(commit=False)
        post.author = request.user
        post.save()
        return redirect('blog:profile', username=request.user.username)
    context = {
        'form': form
    }
    return render(request, 'blog/create.html', context)


@login_required
def edit_post(request, post_id):
    post = get_object_or_404(
        Post,
        pk=post_id
    )

    if request.user != post.author:
        return redirect('blog:post_detail', post_id)
    
    if request.method == 'POST':
        form = CreatePostForm(request.POST, instance=post)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            return redirect('blog:post_detail', post_id)
    else:
        form = CreatePostForm(instance=post)

    context = {
        'form': form
    }
    return render(request, 'blog/create.html', context)


@login_required
def delete_post(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    if request.user != post.author:
        return redirect('blog:post_detail', post_id)
    if request.method == 'POST':
        post.delete()
        return redirect('blog:index')
    form = CreatePostForm(instance=post)
    context = {'form': form}
    return render(request, 'blog/create.html', context)