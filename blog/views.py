from django.contrib.postgres.search import SearchVector
from django.core.mail import send_mail
from django.db.models import Count
from django.shortcuts import render, get_object_or_404
from django.http import Http404
from pyexpat.errors import messages
from .froms import EmailPostForm, CommentForm, SearchForm
from .models import PostModel, CommentModel
from django.core.paginator import Paginator
from django.views.generic import ListView, DetailView
from django.conf import settings
from django.views.decorators.http import require_POST
from taggit.models import Tag


# def post_list(request):
#     post_list = PostModel.published.all()
#     paginator = Paginator(post_list, 5)
#     page = request.GET.get('page',1)
#     posts = paginator.get_page(page)
#     return render(request, 'blog/post/post_list.html', {'posts': posts})


def post_detail(request, year, month, day, slug):
    post = get_object_or_404(PostModel,
                             status=PostModel.Status.PUBLISHED,
                             slug=slug,
                             publish__year=year,
                             publish__month=month,
                             publish__day=day)

    comments = post.comments.filter(active=True)
    form = CommentForm()

    poat_tags_ids = post.tags.values_list('id', flat=True)
    similar_posts = PostModel.published.filter(tags__in=poat_tags_ids).exclude(id=post.id)
    similar_posts = similar_posts.annotate(same_tags=Count('tags')).order_by('-same_tags','-publish')[:4]

    return render(request,
                  'blog/post/detail.html',
                  {'post': post, 'comments': comments, 'form': form, 'similar_posts': similar_posts})


def post_list(request, tag_slug=None):
    post_list = PostModel.published.all()
    tag = None
    if tag_slug:
        tag = get_object_or_404(Tag, slug=tag_slug)
        post_list = post_list.filter(tags__in=[tag])
    paginator = Paginator(post_list, 3)
    page_number = request.GET.get('page', 1)
    try:
        posts = paginator.page(page_number)
    except PageNotAnInteger:
        posts = paginator.page(1)
    except EmptyPage:
        posts = paginator.page(paginator.num_pages)
    return render(request,
                  'blog/post/post_list.html',
                  {'posts': posts,
                   'tag': tag})


# class PostListView(ListView):
#     model = PostModel
#     context_object_name = 'posts'
#     paginate_by = 3
#     template_name = 'blog/post/post_list.html'
#
#     def get_queryset(self):
#         return PostModel.published.all()
#
#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         context['is_paginated'] = True
#         return context


# class PostDetailView(DetailView):
#     model = PostModel
#     context_object_name = 'post'
#     template_name = 'blog/post/detail.html'
#
#     def get_queryset(self):
#         return PostModel.published.all()
#
#     def get_object(self, queryset=None):
#         slug = self.kwargs.get('slug')
#         return get_object_or_404(self.get_queryset(), slug=slug)


def post_share(request, post_id):
    post = get_object_or_404(PostModel, pk=post_id, status=PostModel.Status.PUBLISHED)
    sent = False
    if request.method == 'POST':
        form = EmailPostForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            post_url = request.build_absolute_uri(post.get_absolute_url())
            subject = f"{cd['name']}   {post.title}"
            message = f"Read {post.title}  at {post_url}\n\n {cd['name']}\'s comments: {cd['comments']}"
            send_mail(subject, message, settings.EMAIL_HOST_USER, [cd['to']])
            sent = True
    else:
        form = EmailPostForm()
    return render(request, 'blog/post/share.html', {'post': post, 'form': form, 'sent': sent})


@require_POST
def post_comment(request, post_id):
    post = get_object_or_404(PostModel, pk=post_id, status=PostModel.Status.PUBLISHED)
    comment = None

    form = CommentForm(data=request.POST)

    if form.is_valid():
        comment = form.save(commit=False)
        comment.post = post
        comment.save()

    return render(request, 'blog/post/comment.html', {'post': post, 'form': form, 'comment': comment})


def post_search(request):
    form = SearchForm()
    query = None
    results = []

    if 'query' in request.GET:
        form = SearchForm(request.GET)
        if form.is_valid():
            query = form.cleaned_data['query']
            results = PostModel.published.annotate(
                search=SearchVector('title', 'body')
            ).filter(search=query)

    return render(request,'blog/post/search.html',{'form' : form, 'query' : query,'results':results})
