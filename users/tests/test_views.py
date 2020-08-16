from django.contrib.auth.models import AnonymousUser
from django.test import TestCase
from django.urls import reverse
from users.forms import LoginForm, SignUpForm
from users.models import User

LOGIN_URL = 'auth:login'
SIGN_UP_URL = 'auth:sign_up'
USER_EMAIL = 'user1@user.com'
USER_PASSWORD = 'Password12346789'
USER_NAME = 'user 1'
USER_EMAIL_2 = 'user2@user.com'
USER_PASSWORD_2 = 'Password987654321'
USER_NAME_2 = 'user 2'


class LoginSystem(TestCase):

    def setUp(self):
        User.objects.create_user(email=USER_EMAIL, password=USER_PASSWORD)

    def test_get_login_page(self):
        response = self.client.get(reverse(LOGIN_URL))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'login_page.html')
        self.assertIsInstance(response.context['form'], LoginForm)

    def test_login_user(self):
        response = self.client.post(reverse(LOGIN_URL),
                                    {'email': USER_EMAIL,
                                     'password': USER_PASSWORD}, follow=True)
        self.assertURLEqual(response.redirect_chain[0][0],
                            reverse('main-page'))
        self.assertEquals(response.context['user'].email, USER_EMAIL)

    def test_login_incorrect_data(self):
        response = self.client.post(reverse(LOGIN_URL),
                                    {'email': USER_EMAIL,
                                     'password': USER_PASSWORD_2},
                                    follow=True)
        self.assertURLEqual(response.redirect_chain[0][0], reverse(LOGIN_URL))
        self.assertIsInstance(response.context['user'], AnonymousUser)
        messages = list(response.context['messages'])
        self.assertEquals(str(messages[0]), 'Incorrect email or password')


class SignUpSystem(TestCase):

    def test_get_sign_up_page(self):
        response = self.client.get(reverse(SIGN_UP_URL), follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'sign_up.html')
        self.assertIsInstance(response.context['form'], SignUpForm)

    def test_sign_up_user(self):
        self.assertEqual(User.objects.all().count(), 0)
        response = self.client.post(reverse(SIGN_UP_URL),
                                    {'username': USER_NAME,
                                     'email': USER_EMAIL,
                                     'password': USER_PASSWORD}, follow=True)
        self.assertURLEqual(response.redirect_chain[0][0], reverse(LOGIN_URL))
        self.assertEqual(User.objects.all().count(), 1)
        user = User.objects.get(email=USER_EMAIL)
        self.assertEquals(user.is_moderator, False)
        response = self.client.post(reverse(SIGN_UP_URL),
                                    {'username': USER_NAME_2,
                                     'email': USER_EMAIL_2,
                                     'password': USER_PASSWORD_2,
                                     'moderator': True}, follow=True)
        self.assertEqual(User.objects.all().count(), 2)
        self.assertURLEqual(response.redirect_chain[0][0], reverse(LOGIN_URL))
        user = User.objects.get(email=USER_EMAIL_2)
        self.assertEquals(user.is_moderator, True)

    def test_validate_password(self):
        response = self.client.post(reverse(SIGN_UP_URL),
                                    {'username': USER_NAME,
                                     'email': USER_EMAIL,
                                     'password': 'simple'}, follow=True)
        self.assertEquals(User.objects.all().count(), 0)
        self.assertURLEqual(response.redirect_chain[0][0],
                            reverse(SIGN_UP_URL))
        response = self.client.post(reverse(SIGN_UP_URL),
                                    {'username': USER_NAME,
                                     'email': USER_EMAIL,
                                     'password': '123456789'}, follow=True)
        self.assertEquals(User.objects.all().count(), 0)
        self.assertURLEqual(response.redirect_chain[0][0],
                            reverse(SIGN_UP_URL))

    def test_validate_email(self):
        response = self.client.post(reverse(SIGN_UP_URL),
                                    {'username': USER_NAME,
                                     'email': 'user@user',
                                     'password': USER_PASSWORD}, follow=True)
        self.assertEquals(User.objects.all().count(), 0)
        self.assertURLEqual(response.redirect_chain[0][0],
                            reverse(SIGN_UP_URL))

    def test_sign_up_not_unique_email(self):
        user = User.objects.create_user(email=USER_EMAIL,
                                        password=USER_PASSWORD)
        user.name = USER_NAME
        user.save()
        response = self.client.post(reverse(SIGN_UP_URL),
                                    {'username': USER_NAME_2,
                                     'email': USER_EMAIL,
                                     'password': USER_PASSWORD_2},
                                    follow=True)
        self.assertURLEqual(response.redirect_chain[0][0],
                            reverse(SIGN_UP_URL))
        self.assertEquals(User.objects.all().count(), 1)
