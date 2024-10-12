from wsgiref.validate import validator
from django.utils import timezone
from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify
from django.urls import reverse
from django.utils.translation.template import blankout
from django.core.exceptions import ValidationError
from taggit.managers import TaggableManager

def validate_video_file_size(value):
    max_size = 10 * 1024 * 1024  # Maksimal hajm: 10 MB
    if value.size > max_size:
        raise ValidationError(f'Video hajmi 10 MB dan oshmasligi kerak. Siz yuklagan hajm: {value.size / (1024 * 1024):.2f} MB')

def validate_video_file(value):
    valid_mime_types = ['video/mp4', 'video/avi', 'video/mov']
    file_mime_type = value.file.content_type
    if file_mime_type not in valid_mime_types:
        raise ValidationError('Faqat MP4, AVI yoki MOV formatidagi video fayllar qabul qilinadi.')

def validate_image_file_size(value):
    max_size = 5 * 1024 * 1024  # Maksimal hajm: 5 MB
    if value.size > max_size:
        raise ValidationError(f'Rasm hajmi 5 MB dan oshmasligi kerak. Siz yuklagan hajm: {value.size / (1024 * 1024):.2f} MB')

def validate_image_file_type(value):
    valid_mime_types = ['image/jpeg', 'image/png', 'image/gif']  # Ruxsat etilgan MIME turlari
    file_mime_type = value.file.content_type
    if file_mime_type not in valid_mime_types:
        raise ValidationError('Faqat JPEG, PNG yoki GIF formatidagi rasm fayllarini yuklash mumkin.')


class PublishedManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(status=PostModel.Status.PUBLISHED)


class PostModel(models.Model):

    class Status(models.TextChoices):
        DRAFT = 'DF', 'Draft'
        PUBLISHED = 'PB', 'Published'

    title = models.CharField(max_length=250)
    slug = models.SlugField(max_length=250,unique_for_date='publish')
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    body = models.TextField()
    image = models.ImageField(upload_to="images/",blank=True, null=True)
    video = models.FileField(upload_to="videos/",blank=True, null=True,validators=[validate_video_file_size,validate_video_file])
    publish = models.DateTimeField(default=timezone.now)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    status = models.CharField(max_length=2, choices=Status.choices, default=Status.DRAFT)
    tags = TaggableManager()

    objects = models.Manager()
    published = PublishedManager()

    class Meta:
        ordering = ['-publish']
        verbose_name = 'Post'
        verbose_name_plural = 'Posts'
        get_latest_by = 'publish'
        db_table = 'Posts'
        indexes = [
            models.Index(fields=['-publish']),
        ]

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('blog:post-detail',
                       args=[self.publish.year,
                             self.publish.month,
                             self.publish.day, self.slug])


class CommentModel(models.Model):
    post = models.ForeignKey(PostModel,
                             on_delete=models.CASCADE,
                             related_name='comments')
    name = models.CharField(max_length=80)
    email = models.EmailField()
    body = models.TextField()
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    active = models.BooleanField(default=True)

    class Meta:
        ordering = ['created']
        indexes = [
            models.Index(fields=['created']),
        ]

    def __str__(self):
        return f'Comment by {self.name} on {self.post}'


