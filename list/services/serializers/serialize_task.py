import os
import zipfile
from django.core import serializers


def add_json_in_zip(board_object_list, response):
    file_list = []
    for board in board_object_list:
        task_object_list = board.task_set.all()
        with open("{0}.json".format(board.title), "w") as out:
            file_list.append(out.name)
            out.writelines(serializers.serialize('json', task_object_list))
    zip_file = zipfile.ZipFile(response, 'w')
    for file in file_list:
        file_path = os.path.join(os.getcwd(), file)
        if os.path.exists(file_path):
            zip_file.write(os.path.basename(file_path))
            os.remove(file_path)
    zip_file.close()
