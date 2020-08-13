from list.models import Board


def get_all_boards(user):
    if user.is_moderator or user.is_staff:
        return Board.objects.all()
    else:
        return Board.objects.filter(user_creator=user)
