from django.db.models.signals import m2m_changed, post_delete
from django.dispatch import receiver
from .models import Post
from django.core.mail import send_mail


@receiver(signal=m2m_changed, sender=Post.likes.through)
def users_like_changed(sender, instance, **kwargs):
    instance.total_likes = instance.likes.count()
    instance.save()


@receiver(signal=post_delete, sender=Post)
def send_email_to_delete_post(sender, instance, **kwargs):
    subject = f"Your post has been deleted"
    message = f"Your post has been deleted (Id:{instance.id})"
    send_mail(subject, message, 'danielsadri01@gmail.com', [instance.author.email], True)
