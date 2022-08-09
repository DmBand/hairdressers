from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView

from users_app.models import Hairdresser, City
from .serialazers import CreateUserSerialazer


# TODO ДОСТУПЫ!

class CreateUserAPIView(generics.CreateAPIView):
    """ Регистрация пользователя """
    serializer_class = CreateUserSerialazer

    def post(self, request, *args, **kwargs):
        serialazer = CreateUserSerialazer(data=request.data)
        data = {}
        if serialazer.is_valid():
            serialazer.save()
            username = serialazer.validated_data.get('username')
            data['successful'] = f'Пользователь {username} успешно зарегестрирован!'
            return Response(data, status=status.HTTP_200_OK)
        else:
            data = serialazer.errors
            return Response(data)
