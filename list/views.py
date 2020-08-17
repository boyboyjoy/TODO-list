import os
import zipfile
from datetime import datetime
from django.contrib import messages
from django.http.response import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from list.models import Board, Task, Tag
from list.services.serializers.serialize_task import add_json_in_zip
from list.services.model_handlers.task_object import \
    replace_or_copy_task, create_or_edit_task
from .forms import CreateTaskForm, CreateBoardForm, AddTagForm, ReplaceTaskForm
from .models.choices import TaskStatus
from .services.model_handlers.board_object import create_or_edit_board


def board_list(request):
    if request.user.is_authenticated:
        return render(request, 'board_list.html', {
            'board_list': Board.visible_objects.get(request.user)})
    return redirect(reverse('auth:login'))


def task_list(request, pk):
    if request.user.is_authenticated:
        board = get_object_or_404(Board, pk=pk)
        context = {'task_list': board.task_set.all(), 'board': board,
                   'create_task_form': CreateTaskForm()}
        return render(request, 'task_list.html', context)
    return redirect('main-page')


def create_board(request):
    if request.user.is_authenticated:
        if request.method == 'POST':
            if not create_or_edit_board(request, None):
                return redirect(reverse('create_board'))
        if request.method == 'GET':
            return render(request, 'create_board.html', {
                'create_board_form': CreateBoardForm()})
    return redirect('main-page')


def delete_board(request, pk):
    if request.user.is_authenticated:
        get_object_or_404(Board, pk=pk).delete()
    return redirect('main-page')


def create_task(request, pk):
    if request.user.is_authenticated:
        board = get_object_or_404(Board, pk=pk)
        if request.method == 'GET':
            return render(request, 'create_task.html',
                          {'create_task_form': CreateTaskForm(),
                           'board': board})
        elif request.method == 'POST':
            if create_or_edit_task(request, None, board):
                return redirect(reverse('Board', kwargs={'pk': pk}))
        return redirect(reverse('create_task', kwargs={'pk': pk}))
    return redirect(reverse('main-page'))


def replace_task(request, board_pk, task_pk):
    if request.user.is_authenticated:
        board = get_object_or_404(Board, pk=board_pk)
        if request.method == 'POST':
            replace_or_copy_task(request, Task.objects.get(pk=task_pk),
                                 Board.objects.get(pk=request.POST.get(
                                     'new_parent_board', None)))
            return redirect(reverse('Board', kwargs={'pk': board_pk}))
        elif request.method == 'GET':
            return render(request, 'replace_task.html', {
                'task_pk': task_pk,
                'board': board,
                'replace_task_form': ReplaceTaskForm(
                    Board.visible_objects.get(request.user)),
                'board_list': Board.visible_objects.get(request.user)})
    return redirect('main-page')


def detail_task(request, task_pk, board_pk):
    if request.user.is_authenticated:
        board = get_object_or_404(Board, pk=board_pk)
        task = board.task_set.get(pk=task_pk)
        return render(request, 'detail_task.html', {'task': task,
                                                    'board': board,
                                                    'status': TaskStatus
                                                    (task.task_status).label})
    return redirect('main-page')


def delete_task(request, task_pk, board_pk):
    if request.user.is_authenticated:
        get_object_or_404(Board, pk=board_pk).task_set.get(pk=task_pk).delete()
        return redirect(reverse('Board', kwargs={'pk': board_pk}))
    return redirect('main-page')


def edit_board(request, pk):
    if request.user.is_authenticated:
        board = get_object_or_404(Board, pk=pk)
        if request.method == 'POST':
            if create_or_edit_board(request, board):
                return redirect(reverse('Board', kwargs={'pk': pk}))
            return redirect(reverse('edit_board', kwargs={'pk': pk}))
        elif request.method == 'GET':
            return render(request, 'edit_board.html', {'board': board,
                                                       'edit_board_form':
                                                           CreateBoardForm()})

    return redirect('main-page')


def edit_task(request, board_pk, task_pk):
    if request.user.is_authenticated:
        board = get_object_or_404(Board, pk=board_pk)
        if request.method == 'POST':
            if create_or_edit_task(request, board.task_set.get(pk=task_pk),
                                   None):
                return redirect(reverse('detail_task', kwargs={
                    'board_pk': board_pk,
                    'task_pk': task_pk}))
            return redirect(reverse('edit_task', kwargs={'board_pk': board_pk,
                                                         'task_pk': task_pk}))
        elif request.method == 'GET':
            return render(request, 'edit_task.html', {
                'edit_task_form': CreateTaskForm(), 'board': board,
                'task_pk': task_pk})
    return redirect('main-page')


def get_json(request):
    if request.user.is_authenticated:
        board_object_list = Board.visible_objects.get(request.user)
        if not board_object_list:
            messages.add_message(request, messages.INFO,
                                 "You have not board")
            return redirect(reverse('main-page'))
        response = HttpResponse(content_type='application/zip')
        add_json_in_zip(board_object_list, response)
        response['Content-Disposition'] = f'attachment; filename=' \
                                          f'{str(request.user.name)}.zip'
        return response
    return redirect('main-page')


def get_task_file(request, board_pk, task_pk):
    if request.user.is_authenticated:
        response = HttpResponse(content_type='application/zip')
        zip_file = zipfile.ZipFile(response, 'w')
        task = get_object_or_404(Task, pk=task_pk)
        filepath = os.path.join(os.getcwd(), 'media', str(task.file))
        if os.path.exists(filepath):
            zip_file.write((os.path.relpath(filepath)))
            zip_file.close()
            response['Content-Disposition'] = f'attachment; ' \
                                              f'filename={task.file}.zip'
            return response
    return redirect('main-page')


def add_tag(request, board_pk, task_pk):
    if request.user.is_authenticated:
        board = Board.objects.get(pk=board_pk)
        if request.method == 'POST':
            get_object_or_404(Task, pk=task_pk).tag_set.create(
                text=request.POST.get('tag', None))
            return redirect(reverse('detail_task', kwargs={
                'board_pk': board_pk,
                'task_pk': task_pk}))
        elif request.method == 'GET':
            return render(request, 'add_tag.html', {
                'title_page': 'Add tag',
                'add_tag_form': AddTagForm(),
                'board': board,
                'task_pk': task_pk})
    return redirect('main-page')


def search_task_by_tag(request, tag):
    task_objects_list = []
    if request.user.is_moderator or request.user.is_staff:
        tag_list = Tag.objects.filter(text=tag)
    else:
        tag_list = Tag.objects.filter(
            parent_task__parent_board__user_creator=request.user, text=tag)
    for tag in tag_list:
        task_objects_list.append(tag.parent_task)
    task_objects_list = set(task_objects_list)
    return render(request, 'search_task.html', {
        'task_list': task_objects_list, 'tag': tag})


def complete_task(request, board_pk, task_pk):
    task = get_object_or_404(Task, pk=task_pk)
    if task.task_status == TaskStatus.COMPLETED:
        messages.add_message(request, messages.INFO,
                             'That task has completed already')
        return redirect(reverse('detail_task', kwargs={'board_pk': board_pk,
                                                       'task_pk': task_pk}))
    else:
        task.task_status = TaskStatus.COMPLETED
        task.real_deadline = datetime.today().date()
        task.save()
        return redirect(reverse('detail_task', kwargs={'board_pk': board_pk,
                                                       'task_pk': task_pk}))
