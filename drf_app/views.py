from django.contrib.auth.models import User
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView

from users_app.models import Hairdresser, City, SimpleUser
from .serialazers import (CreateUserSerialazer,
                          UpdateUserSerialazer)


# TODO ДОСТУПЫ!

class CreateUpdateUserAPIView(APIView):
    """ Регистрация и изменение данных простого пользователя """

    def post(self, request, *args, **kwargs):
        serialazer = CreateUserSerialazer(data=request.data)
        data = {}
        if serialazer.is_valid(raise_exception=True):
            serialazer.save()
            username = serialazer.validated_data.get('username')
            data['successful'] = f'Пользователь {username} успешно зарегестрирован!'
            return Response(data, status=status.HTTP_200_OK)
        else:
            data = serialazer.errors
            return Response(data)

    def put(self, request, *args, **kwargs):
        username = kwargs.get('username')
        if not username:
            return Response({'error': 'Username не передан'})
        try:
            instance = User.objects.get(username=username)
        except:
            return Response({'error': f'Пользователь {username} не найден'})

        serialazer = UpdateUserSerialazer(data=request.data, instance=instance)
        serialazer.is_valid(raise_exception=True)
        if 'first_name' not in serialazer.validated_data and 'last_name' not in serialazer.validated_data:
            data = {
                'message': 'Передайте значения параметроа first_name и/или last_name'
            }
            return Response(data, status=status.HTTP_200_OK)

        serialazer.save()
        data = {'successful': f'first_name и/или last_name успешно изменены!'}
        return Response(data, status=status.HTTP_200_OK)

