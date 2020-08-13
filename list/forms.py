import re
from django import forms
from list.models import Task, Board


FILE_SIZE_5_MB = 8388608
COLOR_HEX = '^#([0-9a-fA-F]{6})$'


class CreateBoardForm(forms.ModelForm):
    class Meta:
        model = Board
        fields = ('title', 'color')

    def clean_color(self):
        if not re.fullmatch(COLOR_HEX, self.cleaned_data.get('color')):
            raise forms.ValidationError('Color format is #AAAAAA')
        return self.cleaned_data['color']


class ReplaceTaskForm(forms.Form):
    new_parent_board = forms.ModelChoiceField(queryset=None)

    def __init__(self, board_list):
        super(ReplaceTaskForm, self).__init__()
        self.fields['new_parent_board'].queryset = board_list


class CreateTaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ('description', 'task_status', 'file')

    def clean_file(self):
        file = self.cleaned_data.get('file')
        if file is not None and file.size > FILE_SIZE_5_MB:
            raise forms.ValidationError('File size is bigger than 5 mb')
        else:
            return file


class AddTagForm(forms.Form):
    tag = forms.CharField(max_length=15)
