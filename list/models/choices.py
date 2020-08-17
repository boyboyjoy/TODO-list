from django.db import models


class TaskStatus(models.TextChoices):
    TODO = 'TO', 'TODO'
    STARTED = 'ST', 'STARTED'
    COMPLETED = 'CO', 'COMPLETED'
    CANCELED = 'CA', 'CANCELED'
