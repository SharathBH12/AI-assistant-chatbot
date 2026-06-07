import uuid

from django.db import models
from django.contrib.auth.models import User


class Chat(models.Model):

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE
    )

    title = models.CharField(
        max_length=255
    )

    is_pinned = models.BooleanField(
        default=False
    )

    share_id = models.UUIDField(
        default=uuid.uuid4,
        editable=False,
        null=True,
        blank=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):

        return self.title


class Message(models.Model):

    chat = models.ForeignKey(
        Chat,
        on_delete=models.CASCADE,
        related_name='messages'
    )

    sender = models.CharField(
        max_length=10
    )

    content = models.TextField(
        blank=True
    )

    image = models.ImageField(
        upload_to='chat_images/',
        null=True,
        blank=True
    )

    timestamp = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):

        return f"{self.sender} - {self.chat.title}"