from django import template
from django.db.models import Count
from markdown.core import markdown
from django.utils.safestring import mark_safe
from ..models import PostModel

register = template.Library()


@register.simple_tag(takes_context=True)
def total_posts(context):
    return PostModel.objects.count()


@register.inclusion_tag('blog/post/latest_posts.html')
def show_latest_posts(count=5):
    latest_posts = PostModel.published.order_by('-publish')[:count]
    return {'latest_posts': latest_posts}


@register.simple_tag
def get_most_commented_posts(count=5):
    return PostModel.published.annotate(
        total_comments=Count('comments')
    ).order_by('-total_comments')[:count]

@register.filter(name='markdown')
def markdown_format(text):
    return mark_safe(markdown.markdown(text))
