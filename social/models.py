from django.contrib.auth.models import AbstractUser
from django.db import models
from django.urls import reverse
from taggit.managers import TaggableManager
from django_resized import ResizedImageField
from datetime import datetime


class User(AbstractUser):
    phone_number = models.CharField(max_length=11, blank=True, null=True)
    biography = models.TextField(max_length=500, blank=True, null=True)
    job = models.CharField(max_length=100, blank=True, null=True)
    date_of_birth = models.DateField(blank=True, null=True)
    photo = models.ImageField(upload_to='images/', blank=True, null=True)
    following = models.ManyToManyField('self', through="Contact", related_name="followers", symmetrical=False)

    def get_absolute_url(self):
        return reverse("social:user_detail", args=[self.username])


class Post(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='posts')
    description = models.TextField(max_length=500)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    likes = models.ManyToManyField(User, related_name="liked_posts", blank=True)
    saved_by = models.ManyToManyField(User, related_name='saved_posts', blank=True)
    total_likes = models.PositiveBigIntegerField(default=0)
    active = models.BooleanField(default=True)
    tags = TaggableManager()

    class Meta:
        ordering = ['-created']
        indexes = [
            models.Index(fields=['-created']),
            models.Index(fields=['-total_likes']),
        ]

    def __str__(self):
        return self.author.username

    def get_absolute_url(self):
        return reverse('social:post_detail', kwargs={'post_id': self.id})

    def delete(self, *args, **kwargs):
        for image in self.images.all():
            storage, path = image.image_file.storage, image.image_file.path
            storage.delete(path)
        super().delete(*args, **kwargs)


def get_image_file(instance, filename):
    return f"post_images/{datetime.now().strftime('%Y/%m/%d')}/{filename}"


class Image(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='images')
    image_file = ResizedImageField(upload_to=get_image_file, size=[600, 400], crop=['middle', 'center'], quality=100)
    title = models.CharField(max_length=100, blank=True, null=True)
    description = models.TextField(max_length=500, blank=True, null=True)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created']
        indexes = [
            models.Index(fields=['-created'])
        ]

    def __str__(self):
        return self.title if self.title else self.image_file.name

    def delete(self, *args, **kwargs):
        storage, path = self.image_file.storage, self.image_file.path
        storage.delete(path)
        super().delete(*args, **kwargs)


class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    description = models.TextField(max_length=300)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created']
        indexes = [
            models.Index(fields=['-created'])
        ]

    def __str__(self):
        return self.description[:20]


class Contact(models.Model):
    user_from = models.ForeignKey(User, on_delete=models.CASCADE, related_name="rel_from_set")
    user_to = models.ForeignKey(User, on_delete=models.CASCADE, related_name="rel_to_set")
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created']
        indexes = [models.Index(fields=['-created'])]

    def __str__(self):
        return f"{self.user_from} follows {self.user_to}"
