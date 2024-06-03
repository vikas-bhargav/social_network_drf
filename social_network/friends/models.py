"""This module provides models for the Friends app."""
from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    """Friends user model."""
    email = models.EmailField(unique=True, max_length=100)
    friends = models.ManyToManyField("User", blank=True,
                                     related_name="user_friends",
                                     )
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    @property
    def get_fullname(self) -> str:
        """Return user's full name.'"""
        return str(self.first_name + " " + self.last_name).strip()

    def __str__(self) -> str:
        """Return user email."""
        return str(self.email)


class StatusType:
    """Types of request status."""

    PENDING = 'pending'
    ACCEPTED = 'accepted'
    REJECTED = 'rejected'
    CHOICES = [
        (PENDING, 'Pending'),
        (ACCEPTED, 'Accepted'),
        (REJECTED, 'Rejected')
    ]


class FriendRequest(models.Model):
    """FriendRequest model for Friends app."""
    from_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="from_user")
    to_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="to_user")
    status = models.CharField(
        choices=StatusType.CHOICES,
        default=StatusType.PENDING,
        max_length=10
    )

    class Meta:
        constraints = [models.UniqueConstraint(fields=['from_user', 'to_user'], name='Unique friend request')]
