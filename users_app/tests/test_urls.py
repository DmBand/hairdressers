from django.test import TestCase
from django.urls import resolve
from ..views import homepage_view


class HomePageTest(TestCase):

    def test_homepage_url(self):
        found = resolve('/')
        self.assertEquals(found.func, homepage_view)
