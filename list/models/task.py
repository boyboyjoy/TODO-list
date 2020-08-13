from django.db import models
from list.models.board import Board


class TaskStatus(models.TextChoices):
    TODO = 'TO', 'TODO'
    STARTED = 'ST', 'STARTED'
    COMPLETED = 'CO', 'COMPLETED'
    CANCELED = 'CA', 'CANCELED'


class Task(models.Model):
    description = models.TextField(max_length=200, blank=False)
    scheduled_deadline = models.DateField(auto_now_add=False)
    real_deadline = models.DateField(auto_now_add=True)
    task_status = models.CharField(max_length=2, choices=TaskStatus.choices,
                                   default=TaskStatus.TODO)
    file = models.FileField(default=None, blank=True)
    parent_board = models.ForeignKey(Board, on_delete=models.CASCADE,
                                     default=None)

    def __str__(self):
        return self.description

    class Meta:
        db_table = 'Task'
        app_label = 'list'
