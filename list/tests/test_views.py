from datetime import datetime
from django.test import TestCase
from django.urls import reverse
from list.forms import CreateBoardForm, CreateTaskForm, ReplaceTaskForm, AddTagForm
from list.models import Board
from list.models.task import TaskStatus
from users.models import User

LOGIN_URL = 'auth:login'
SIGN_UP_URL = 'auth:sign_up'
USER_EMAIL = 'user1@user.com'
USER_PASSWORD = 'Password12346789'
USER_NAME = 'user 1'
ADMIN_EMAIL = 'user2@user.com'
ADMIN_PASSWORD = 'Password987654321'
USER_NAME_2 = 'user 2'


class MainPage(TestCase):
    def setUp(self):
        User.objects.create_user(email=USER_EMAIL, password=USER_PASSWORD)
        User.objects.create_user(email=ADMIN_EMAIL, password=ADMIN_PASSWORD)
        admin = User.objects.get(email=ADMIN_EMAIL)
        user = User.objects.get(email=USER_EMAIL)
        admin.is_moderator = True
        admin.save()
        for i in range(0, 3):
            admin.board_set.create(title='admin-board {0}'.format(i))
        for i in range(0, 3):
            user.board_set.create(title='user-board {0}'.format(i))

    def test_get_board_list_page(self):
        user = User.objects.get(email=USER_EMAIL)
        self.client.login(email=USER_EMAIL, password=USER_PASSWORD)
        response = self.client.get(reverse('main-page'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'board_list.html')
        self.assertTrue(list(response.context['board_list']) ==
                        list(Board.objects.filter(user_creator=user)))

    def test_visibility_alien_boards(self):
        self.client.login(email=USER_EMAIL, password=USER_PASSWORD)
        user = User.objects.get(email=USER_EMAIL)
        response = self.client.get(reverse('main-page'))
        self.assertTrue(list(response.context['board_list']),
                        list(Board.objects.filter(user_creator=user)))
        self.client.logout()
        self.client.login(email=ADMIN_EMAIL, password=ADMIN_PASSWORD)
        response = self.client.get(reverse('main-page'))
        self.assertTrue(list(response.context['board_list']),
                        list(Board.objects.all()))

    def test_get_json(self):
        self.client.login(email=USER_EMAIL, password=USER_PASSWORD)
        user = User.objects.get(email=USER_EMAIL)
        response = self.client.get(reverse('get_json'))
        self.assertEquals(
            response.get('Content-Disposition'),
            "attachment; filename={0}.zip".format(user.name))

    def test_have_not_tasks_for_json(self):
        self.client.login(email=USER_EMAIL, password=USER_PASSWORD)
        user = User.objects.get(email=USER_EMAIL)
        for board in Board.objects.filter(user_creator=user):
            board.delete()
        response = self.client.get(reverse('get_json'))
        self.assertEquals(response.get('Content-Disposition'), None)

    def test_get_create_board_page(self):
        self.client.login(email=USER_EMAIL, password=USER_PASSWORD)
        response = self.client.get(reverse('create_board'))
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'create_board.html')
        self.assertIsInstance(response.context['create_board_form'],
                              CreateBoardForm)

    def test_create_board(self):
        self.client.login(email=USER_EMAIL, password=USER_PASSWORD)
        response = self.client.get(reverse('main-page'))
        self.assertEqual(response.context['board_list'].count(), 3)
        response = self.client.post(reverse('create_board'),
                                    {'title': 'new_board',
                                     'color': '#AAABBB'},
                                    follow=True)
        self.assertURLEqual(response.redirect_chain[0][0],
                            reverse('main-page'))
        self.assertEqual(response.context['board_list'].count(), 4)

    def test_validate_board_color(self):
        self.client.login(email=USER_EMAIL, password=USER_PASSWORD)
        self.client.post(reverse('create_board'),
                         {'title': 'new_board', 'color': '1231231'},
                         follow=True)
        self.assertEqual(Board.objects.all().count(), 6)
        self.client.post(reverse('create_board'),
                         {'title': 'new_board', 'color': '#AQAQAQ'},
                         follow=True)
        self.assertEqual(Board.objects.all().count(), 6)

    def test_logout_system(self):
        self.client.login(email=USER_EMAIL, password=USER_PASSWORD)
        response = self.client.get(reverse('main-page'))
        self.assertIsInstance(response.context['user'], User)
        self.client.get(reverse('auth:logout'))
        response = self.client.get(reverse('main-page'), follow=True)
        self.assertURLEqual(response.redirect_chain[0][0],
                            reverse('auth:login'))


class TaskListPage(TestCase):
    def setUp(self):
        User.objects.create_user(email=USER_EMAIL, password=USER_PASSWORD)
        User.objects.create_user(email=ADMIN_EMAIL, password=ADMIN_PASSWORD)
        admin = User.objects.get(email=ADMIN_EMAIL)
        user = User.objects.get(email=USER_EMAIL)
        admin.is_moderator = True
        admin.save()
        admin_board = admin.board_set.create(title='admin-board')
        user_board = user.board_set.create(title='user-board')
        user_board.task_set.create(description='test_task',
                                   scheduled_deadline='2025-10-10',
                                   real_deadline='2024-10-10',
                                   task_status=TaskStatus.STARTED)
        admin_board.task_set.create(description='test_task',
                                    scheduled_deadline='2025-10-10',
                                    real_deadline='2024-10-10',
                                    task_status=TaskStatus.STARTED)

    def test_get_task_page(self):
        self.client.login(email=USER_EMAIL, password=USER_PASSWORD)
        user = User.objects.get(email=USER_EMAIL)
        board = Board.objects.filter(user_creator=user)[0]
        response = self.client.get(reverse('Board', kwargs={'pk': board.id}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'task_list.html')
        self.assertEqual(list(response.context['task_list']),
                         list(board.task_set.all()))

    def test_delete_board(self):
        self.client.login(email=USER_EMAIL, password=USER_PASSWORD)
        user = User.objects.get(email=USER_EMAIL)
        board = Board.objects.filter(user_creator=user)[0]
        self.assertEqual(Board.objects.filter(user_creator=user).count(), 1)
        response = self.client.get(reverse('delete_board',
                                           kwargs={'pk': board.id}),
                                   follow=True)
        self.assertURLEqual(response.redirect_chain[0][0],
                            reverse('main-page'))
        self.assertEqual(Board.objects.filter(user_creator=user).count(), 0)

    def test_get_edit_board_page(self):
        self.client.login(email=USER_EMAIL, password=USER_PASSWORD)
        user = User.objects.get(email=USER_EMAIL)
        board = Board.objects.filter(user_creator=user)[0]
        response = self.client.get(reverse('edit_board',
                                           kwargs={'pk': board.id}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'edit_board.html')
        self.assertIsInstance(response.context['edit_board_form'],
                              CreateBoardForm)

    def test_edit_board(self):
        self.client.login(email=USER_EMAIL, password=USER_PASSWORD)
        user = User.objects.get(email=USER_EMAIL)
        board = Board.objects.filter(user_creator=user)[0]
        response = self.client.post(reverse('edit_board',
                                            kwargs={'pk': board.id}),
                                    {'title': 'NewBoardTitle',
                                     'color': '#AAAAAA'}, follow=True)
        self.assertEquals(Board.objects.filter(user_creator=user)[0].title,
                          'NewBoardTitle')
        self.assertURLEqual(response.redirect_chain[0][0],
                            reverse('Board', kwargs={'pk': board.id}))

    def test_validate_color_edit_board(self):
        self.client.login(email=USER_EMAIL, password=USER_PASSWORD)
        user = User.objects.get(email=USER_EMAIL)
        board = Board.objects.filter(user_creator=user)[0]
        response = self.client.post(reverse('edit_board',
                                            kwargs={'pk': board.id}),
                                    {'title': 'NewBoardTitle',
                                     'color': '1231231'}, follow=True)
        self.assertURLEqual(response.redirect_chain[0][0],
                            reverse('edit_board', kwargs={'pk': board.id}))
        self.assertEqual(board.color, '#AAAAAA')
        response = self.client.post(reverse('edit_board',
                                            kwargs={'pk': board.id}),
                                    {'title': 'NewBoardTitle',
                                     'color': '#ZAAAAA'}, follow=True)
        self.assertURLEqual(response.redirect_chain[0][0],
                            reverse('edit_board', kwargs={'pk': board.id}))
        self.assertEqual(board.color, '#AAAAAA')

    def test_get_create_task_page(self):
        self.client.login(email=USER_EMAIL, password=USER_PASSWORD)
        user = User.objects.get(email=USER_EMAIL)
        user_board = Board.objects.filter(user_creator=user)[0]
        response = self.client.get(reverse('create_task',
                                           kwargs={'pk': user_board.id}),
                                   follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'create_task.html')
        self.assertIsInstance(response.context['create_task_form'],
                              CreateTaskForm)

    def test_create_task(self):
        self.client.login(email=USER_EMAIL, password=USER_PASSWORD)
        user = User.objects.get(email=USER_EMAIL)
        board = Board.objects.filter(user_creator=user)[0]
        self.assertEqual(board.task_set.all().count(), 1)
        response = self.client.post(reverse('create_task', kwargs={
            'pk': board.id}), {'description': 'ggwp',
                               'scheduled_deadline': '2024-10-10',
                               'task_status': TaskStatus.STARTED},
                                    follow=True)
        self.assertEqual(board.task_set.all().count(), 2)
        self.assertURLEqual(response.redirect_chain[0][0],
                            reverse('Board', kwargs={'pk': board.id}))

    def test_validate_deadline_task(self):
        self.client.login(email=USER_EMAIL, password=USER_PASSWORD)
        user = User.objects.get(email=USER_EMAIL)
        board = Board.objects.filter(user_creator=user)[0]
        self.assertEqual(board.task_set.all().count(), 1)
        response = self.client.post(reverse('create_task', kwargs={
            'pk': board.id}), {'description': 'ggwp',
                               'scheduled_deadline': '2019-10-10',
                               'task_status': TaskStatus.STARTED},
                                    follow=True)
        self.assertEqual(board.task_set.all().count(), 1)
        self.assertURLEqual(response.redirect_chain[0][0],
                            reverse('create_task', kwargs={'pk': board.id}))

    def test_empty_deadline_task(self):
        self.client.login(email=USER_EMAIL, password=USER_PASSWORD)
        user = User.objects.get(email=USER_EMAIL)
        board = Board.objects.filter(user_creator=user)[0]
        self.assertEqual(board.task_set.all().count(), 1)
        response = self.client.post(reverse('create_task', kwargs={
            'pk': board.id}), {'description': 'ggwp',
                               'scheduled_deadline': '',
                               'task_status': TaskStatus.STARTED},
                                    follow=True)
        self.assertEqual(board.task_set.all().count(), 1)
        self.assertURLEqual(response.redirect_chain[0][0],
                            reverse('create_task', kwargs={'pk': board.id}))


class DetailTaskPage(TestCase):

    def setUp(self):
        User.objects.create_user(email=USER_EMAIL, password=USER_PASSWORD)
        User.objects.create_user(email=ADMIN_EMAIL, password=ADMIN_PASSWORD)
        admin = User.objects.get(email=ADMIN_EMAIL)
        admin.is_moderator = True
        admin.save()
        admin_board = admin.board_set.create(title='admin-board')
        user = User.objects.get(email=USER_EMAIL)
        user_board = user.board_set.create(title='user-board')
        user_board.task_set.create(description='test_task',
                                   scheduled_deadline='2020-10-10',
                                   real_deadline='2020-10-10',
                                   task_status=TaskStatus.STARTED)
        admin_board.task_set.create(description='test_task',
                                    scheduled_deadline='2020-10-10',
                                    real_deadline='2020-10-10',
                                    task_status=TaskStatus.STARTED)

    def test_get_task_detail_page(self):
        self.client.login(email=USER_EMAIL, password=USER_PASSWORD)
        board = Board.objects.all()[0]
        task = board.task_set.all()[0]
        response = self.client.get(reverse('detail_task', kwargs={
            'board_pk': board.id, 'task_pk': task.id}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'detail_task.html')
        self.assertEqual(response.context['task'], task)

    def test_get_edit_task_page(self):
        self.client.login(email=USER_EMAIL, password=USER_PASSWORD)
        board = Board.objects.all()[0]
        task = board.task_set.all()[0]
        response = self.client.get(reverse('edit_task', kwargs={
            'board_pk': board.id, 'task_pk': task.id}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'edit_task.html')
        self.assertIsInstance(response.context['edit_task_form'],
                              CreateTaskForm)

    def test_deadline_validate_edit_task(self):
        self.client.login(email=USER_EMAIL, password=USER_PASSWORD)
        board = Board.objects.all()[0]
        task = board.task_set.all()[0]
        old_deadline = task.scheduled_deadline
        response = self.client.post(reverse('edit_task', kwargs={
            'board_pk': board.id, 'task_pk': task.id}),
                                    {'description': 'new_description',
                                     'scheduled_deadline': '2019-12-12',
                                     'task_status': TaskStatus.STARTED},
                                    follow=True)
        self.assertEqual(task.scheduled_deadline, old_deadline)
        self.assertURLEqual(response.redirect_chain[0][0],
                            reverse('edit_task', kwargs={'board_pk': board.id,
                                                         'task_pk': task.id}))

    def test_empty_deadline_edit_task(self):
        self.client.login(email=USER_EMAIL, password=USER_PASSWORD)
        board = Board.objects.all()[0]
        task = board.task_set.all()[0]
        old_deadline = task.scheduled_deadline
        response = self.client.post(reverse('edit_task', kwargs={
            'board_pk': board.id, 'task_pk': task.id}),
                                    {'description': 'new_description',
                                     'scheduled_deadline': '',
                                     'task_status': TaskStatus.STARTED},
                                    follow=True)
        self.assertEqual(task.scheduled_deadline, old_deadline)
        self.assertURLEqual(response.redirect_chain[0][0],
                            reverse('edit_task', kwargs={'board_pk': board.id,
                                                         'task_pk': task.id}))

    def test_edit_task(self):
        self.client.login(email=USER_EMAIL, password=USER_PASSWORD)
        board = Board.objects.all()[0]
        task = board.task_set.all()[0]
        response = self.client.post(reverse('edit_task', kwargs={
            'board_pk': board.id, 'task_pk': task.id}),
                                    {'description': 'new_description',
                                     'scheduled_deadline': '2024-12-12',
                                     'task_status': TaskStatus.TODO},
                                    follow=True)
        task = board.task_set.all()[0]
        self.assertEqual(task.scheduled_deadline,
                         datetime(2024, 12, 12).date())
        self.assertEqual(task.task_status, TaskStatus.TODO)
        self.assertEqual(task.description, 'new_description')
        self.assertURLEqual(response.redirect_chain[0][0],
                            reverse('detail_task', kwargs={
                                'board_pk': board.id, 'task_pk': task.id}))

    def test_get_replace_copy_task_page(self):
        self.client.login(email=USER_EMAIL, password=USER_PASSWORD)
        board = Board.objects.all()[0]
        task = board.task_set.all()[0]
        response = self.client.get(reverse('replace_task', kwargs={
            'board_pk': board.id, 'task_pk': task.id}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'replace_task.html')
        self.assertIsInstance(response.context['replace_task_form'],
                              ReplaceTaskForm)

    def test_replace_task(self):
        self.client.login(email=USER_EMAIL, password=USER_PASSWORD)
        board = Board.objects.get(title='user-board')
        task = board.task_set.all()[0]
        Board(user_creator=User.objects.get(email=USER_EMAIL),
              title='ReplacingBoard', color='#AAABBB').save()
        new_board = Board.objects.get(title='ReplacingBoard')
        self.assertEqual(board.task_set.all().count(), 1)
        response = self.client.post(reverse('replace_task', kwargs={
            'board_pk': board.id, 'task_pk': task.id}), {
                                        'new_parent_board': new_board.id,
                                        'replace': ['replace']}, follow=True)
        self.assertEqual(board.task_set.all().count(), 0)
        self.assertEqual(new_board.task_set.all().count(), 1)
        self.assertURLEqual(response.redirect_chain[0][0],
                            reverse('Board', kwargs={'pk': board.id}))

    def test_copy_task(self):
        self.client.login(email=USER_EMAIL, password=USER_PASSWORD)
        board = Board.objects.get(title='user-board')
        task = board.task_set.all()[0]
        Board(user_creator=User.objects.get(email=USER_EMAIL),
              title='ReplacingBoard', color='#AAABBB').save()
        self.assertEqual(board.task_set.all().count(), 1)
        response = self.client.post(reverse('replace_task', kwargs={
            'board_pk': board.id, 'task_pk': task.id}), {
                                        'new_parent_board': board.id,
                                        'copy': ['copy']}, follow=True)
        self.assertEqual(board.task_set.all().count(), 2)
        self.assertURLEqual(response.redirect_chain[0][0],
                            reverse('Board', kwargs={'pk': board.id}))

    def search_by_tag(self):
        self.client.login(email=USER_EMAIL, password=USER_PASSWORD)
        user = User.objects.get(email=USER_EMAIL)
        board = Board.objects.get(title='user-board')
        task = board.task_set.all()[0]
        board_2 = Board.objects.create(user_creator=user, title='2nd board',
                                       color='#AAABBB')
        task_2 = board_2.task_set.create(description='new_task',
                                         scheduled_deadline='2020-12-12',
                                         task_status=TaskStatus.STARTED)
        task.tag_set.create(text='default')
        task_2.tag_set.create(text='default')
        response = self.client.get(reverse('search_tag', kwargs={'default'}))
        task_list = [task, task_2]
        self.assertEqual(response.context['task_list'], task_list)

    def test_get_add_tag_page(self):
        self.client.login(email=USER_EMAIL, password=USER_PASSWORD)
        user = User.objects.get(email=USER_EMAIL)
        board = user.board_set.all()[0]
        task = board.task_set.all()[0]
        response = self.client.get(reverse('add_tag', kwargs={
            'board_pk': board.id, 'task_pk': task.id}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'add_tag.html')
        self.assertIsInstance(response.context['add_tag_form'], AddTagForm)

    def test_add_tag(self):
        self.client.login(email=USER_EMAIL, password=USER_PASSWORD)
        user = User.objects.get(email=USER_EMAIL)
        board = user.board_set.all()[0]
        task = board.task_set.all()[0]
        response = self.client.post(reverse('add_tag', kwargs={
            'board_pk': board.id, 'task_pk': task.id}), {'tag': 'new_tag'},
                                    follow=True)
        self.assertURLEqual(response.redirect_chain[0][0], reverse(
            'detail_task', kwargs={'board_pk': board.id, 'task_pk': task.id}))
        self.assertEqual(task.tag_set.all().count(), 1)

    def test_complete_task(self):
        self.client.login(email=USER_EMAIL, password=USER_PASSWORD)
        user = User.objects.get(email=USER_EMAIL)
        board = user.board_set.all()[0]
        task = board.task_set.all()[0]
        self.client.post(reverse('complete_task', kwargs={
            'board_pk': board.id, 'task_pk': task.id}),
                         follow=True)
        task = board.task_set.all()[0]
        self.assertEqual(task.task_status, TaskStatus.COMPLETED)

    def test_delete_task(self):
        self.client.login(email=USER_EMAIL, password=USER_PASSWORD)
        user = User.objects.get(email=USER_EMAIL)
        board = user.board_set.all()[0]
        task = board.task_set.all()[0]
        self.assertEqual(board.task_set.all().count(), 1)
        response = self.client.post(reverse('delete_task', kwargs={
            'board_pk': board.id, 'task_pk': task.id}),
                                    follow=True)
        self.assertEqual(board.task_set.all().count(), 0)
        self.assertURLEqual(response.redirect_chain[0][0], reverse(
            'Board', kwargs={'pk': board.id}))
