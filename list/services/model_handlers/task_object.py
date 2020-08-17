from datetime import datetime
from django.core.exceptions import ValidationError
from list.forms import CreateTaskForm
from list.models import Task
from django.contrib import messages
from list.services.validators.task_validators import date_validate


def replace_or_copy_task(request, task, new_parent_board):
    if 'replace' in request.POST:
        task.parent_board = new_parent_board
        task.save()
    elif 'copy' in request.POST:
        copy_task = Task(parent_board=new_parent_board,
                         description=task.description,
                         scheduled_deadline=task.scheduled_deadline,
                         real_deadline=task.real_deadline,
                         task_status=task.task_status)
        copy_task.save()
        for tag in task.tag_set.all():
            copy_task.tag_set.create(text=tag.text)


def create_or_edit_task(request, task, parent_board):
    form = CreateTaskForm(request.POST, request.FILES)
    try:
        date_validate(request.POST.get('scheduled_deadline', None))
    except ValidationError as error:
        messages.add_message(request, messages.INFO, str(error)[2:-2])
        return
    if form.is_valid():
        if task is None:
            task = Task(parent_board=parent_board)
        task.description = request.POST.get('description', None)
        task.scheduled_deadline = request.POST.get('scheduled_deadline',
                                                   None)
        task.real_deadline = datetime.today().date()
        task.task_status = request.POST.get('task_status', None)
        task.file = form.cleaned_data['file']
        task.save()
        return task
    for error in form.errors:
        messages.add_message(request, messages.INFO, form.errors[error])
