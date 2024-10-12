from django.contrib import admin
from .models import PostModel, CommentModel

@admin.register(PostModel)
class PostAdmin(admin.ModelAdmin):
    list_display = ('title', 'slug', 'author', 'publish')
    list_filter = ('publish',)
    search_fields = ('title', 'slug')
    date_hierarchy = 'publish'
    raw_id_fields = ('author',)
    ordering = ['publish']
    prepopulated_fields = {"slug": ("title",)}


@admin.register(CommentModel)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('name','email','post', 'created','active')
    list_filter = ('active','created','updated')
    search_fields = ('email','body','name')



