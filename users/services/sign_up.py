from django.contrib import messages
from users.forms import SignUpForm
from users.models import User


def create_user(request):
    form = SignUpForm(request.POST)
    if form.is_valid():
        user = User.objects.create_user(email=request.POST.get('email', None),
                                        password=request.POST.get('password',
                                                                  None))
        user.name = request.POST.get('username', None)
        if request.POST.get('moderator', None):
            user.is_moderator = True
        user.save()
        return user
    for error in form.errors:
        messages.add_message(request, messages.INFO, form.errors[error])
