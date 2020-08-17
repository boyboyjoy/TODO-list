from django.contrib import messages
from list.forms import CreateBoardForm
from list.models import Board


def create_or_edit_board(request, board=None):
    if board is None:
        board = Board(user_creator=request.user)
    form = CreateBoardForm(request.POST)
    if form.is_valid():
        board.title = request.POST.get('title', None)
        board.color = form.cleaned_data['color']
        board.save()
        return board
    for error in form.errors:
        messages.add_message(request, messages.INFO, form.errors[error])
