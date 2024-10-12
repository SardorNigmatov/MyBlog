from django.urls import path
from .views import post_list, post_detail, post_share, post_comment, post_search

app_name = 'blog'

urlpatterns = [
    path('', post_list, name='post-list'),
    path('<int:year>/<int:month>/<int:day>/<slug:slug>/',post_detail, name='post-detail'),
    path('<int:post_id>/share/',post_share,name='post-share'),
    path('<int:post_id>/comment/',post_comment,name='post-comment'),
    path('tag/<slug:tag_slug>/',post_list, name='post_list_by_tag'),
    path('search/',post_search, name='post-search'),
]