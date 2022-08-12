from django.contrib.auth.models import User
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from users_app.models import Hairdresser, City, SimpleUser
from .permissons import IsOwnerOrReadOnly
from .serialazers import (CreateUserSerialazer,
                          UpdateUserSerialazer,
                          SimpleUserSerialazer)


# TODO ДОСТУПЫ!

class CreateUserAPIView(APIView):
    """ Регистрация пользователя """

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


class UpdateDeleteUserAPIView(APIView):
    """ Изменение и удаление данных пользователя """

    permission_classes = (
        IsAuthenticated,
        IsOwnerOrReadOnly,
    )

    def get(self, request, *args, **kwargs):
        username = kwargs.get('username')
        if not username:
            return Response({'error': 'Username не передан'})
        instance = User.objects.filter(username=username).first()
        if not instance:
            return Response({'error': f'Пользователь {username} не найден'})
        self.check_object_permissions(request=request, obj=instance)
        data = SimpleUserSerialazer(instance.simpleuser)
        return Response(data.data)

    def put(self, request, *args, **kwargs):
        username = kwargs.get('username')
        if not username:
            return Response({'error': 'Username не передан'})

        instance = User.objects.filter(username=username).first()
        if not instance:
            return Response({'error': f'Пользователь {username} не найден'})

        self.check_object_permissions(request=request, obj=instance)
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

    def delete(self, request, *args, **kwargs):
        # TODO досуп!
        username = kwargs.get('username')
        if not username:
            return Response({'error': 'Username не передан'})

        user = User.objects.filter(username=username).first()
        if not user:
            return Response({'error': f'Пользователь {username} не найден'})

        self.check_object_permissions(request=request, obj=user)
        user.delete()
        data = {'successful': f'Пользователь {username} успешно удален!'}
        return Response(data, status=status.HTTP_200_OK)


class CreateUpdateHairdresserAPIView(APIView):
    def post(self, request, *args, **kwargs):
        pass
