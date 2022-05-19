from django.test import TestCase

from users_app.models import SimpleUser, User, Hairdresser


class SimpleUserModelTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        user = User.objects.create()
        simple_user = SimpleUser.objects.create(owner=user)
        Hairdresser.objects.create(owner=simple_user)

    def test_max_field_length_simpleuser(self):
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

    def test_max_field_length_hairdresser(self):
        """
        Checking the maximum length of a hairdresser model fields
        """

        hairdresser = Hairdresser.objects.get(id=1)
        instagram = hairdresser._meta.get_field('instagram').max_length
        another_info = hairdresser._meta.get_field('another_info').max_length
        self.assertEquals(instagram, 100)
        self.assertEquals(another_info, 1000)
