from django.db import models


class BoardManager(models.Manager):
    def get(self, user):
        if user.is_moderator or user.is_staff:
            return super().get_queryset()
        else:
            return super().get_queryset().filter(user_creator=user)
