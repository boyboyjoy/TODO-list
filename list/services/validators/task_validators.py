from datetime import datetime
from django.core.exceptions import ValidationError


def date_validate(scheduled_deadline):
    if not scheduled_deadline:
        raise ValidationError('Input deadline')
    if str(datetime.today().date()) >= scheduled_deadline:
        raise ValidationError('Deadline should be tomorrow or later')
