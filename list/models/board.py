from django.db import models
from users.models import User


class Board(models.Model):
    title = models.CharField(max_length=30, blank=False)
    user_creator = models.ForeignKey(User, on_delete=models.CASCADE)
    color = models.CharField(max_length=7, blank=False, default='#AAAAAA')

    def __str__(self):
        return self.title

    class Meta:
        db_table = 'Board'
        app_label = 'list'
