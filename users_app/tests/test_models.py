from django.test import TestCase

from users_app.models import SimpleUser, User, Hairdresser


class SimpleUserModelTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        user = User.objects.create(
            username='test',
            first_name='test',
            last_name='test',
            email='test@mail.ru'
        )

        simple_user = SimpleUser.objects.create(
            username=user.username,
            name=user.first_name,
            surname=user.last_name,
            email=user.email,
            slug=user.username,
            owner=user
        )

    def test_max_field_length(self):
        """
        Checking the maximum length of a simpleuser model fields
        """

        s_user = SimpleUser.objects.get(id=1)
        fields = ['username', 'name', 'surname', 'slug']
        length = {f: s_user._meta.get_field(f).max_length for f in fields}
        for len_ in length:
            if len_ == 'username':
                self.assertEquals(length[len_], 30)
            else:
                self.assertEquals(length[len_], 50)
