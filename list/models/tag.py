from django.db import models
from list.models.task import Task


class Tag(models.Model):
    text = models.CharField(max_length=15, blank=False, default=None)
    parent_task = models.ForeignKey(Task, on_delete=models.CASCADE,
                                    default=None)

    class Meta:
        db_table = 'Tag'
        app_label = 'list'

    def __str__(self):
        return self.text
