from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from users_app.models import Hairdresser
from .permissons import IsOwner
from .serialazers import (CreateUserSerialazer,
                          UpdateUserSerialazer,
                          SimpleUserSerialazer,
                          GetHairdresserSerialazer,
                          CreateHairdresserSerialazer)


# TODO ДОСТУПЫ!
# TODO ЗАГРУЗКА ФОТО!

class CreateUserAPIView(APIView):
    """ Регистрация пользователя """

    def post(self, request, **kwargs):
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
        IsOwner,
    )

    def get(self, request, **kwargs):
        username = kwargs.get('username')
        user = User.objects.filter(username=username).first()
        if not user:
            return Response({'error': f'Пользователь {username} не найден'})

        self.check_object_permissions(
            request=request,
            obj=user
        )
        data = SimpleUserSerialazer(user.simpleuser)
        return Response(data.data)

    def put(self, request, **kwargs):
        username = kwargs.get('username')
        user = User.objects.filter(username=username).first()
        if not user:
            return Response({'error': f'Пользователь {username} не найден'})

        self.check_object_permissions(
            request=request,
            obj=user
        )
        serialazer = UpdateUserSerialazer(
            data=request.data,
            instance=user
        )
        serialazer.is_valid(raise_exception=True)
        if 'first_name' not in serialazer.validated_data and 'last_name' not in serialazer.validated_data:
            data = {
                'message': 'Передайте значения параметроа first_name и/или last_name'
            }
            return Response(data, status=status.HTTP_200_OK)

        serialazer.save()
        data = {'successful': f'first_name и/или last_name успешно изменены!'}
        return Response(data, status=status.HTTP_200_OK)

    def delete(self, request, **kwargs):
        username = kwargs.get('username')
        user = User.objects.filter(username=username).first()
        if not user:
            return Response({'error': f'Пользователь {username} не найден'})

        self.check_object_permissions(
            request=request,
            obj=user
        )
        user.delete()
        data = {'successful': f'Пользователь {username} успешно удален!'}
        return Response(data, status=status.HTTP_200_OK)


class CreateHairdresserAPIView(APIView):
    """ Создание парикмахера """
    permission_classes = (
        IsAuthenticated,
    )

    def post(self, request):
        user = request.user.simpleuser
        if user.is_hairdresser:
            hairdresser = Hairdresser.objects.get(owner=user)
            serialazer = GetHairdresserSerialazer(hairdresser)
            data = {
                'error': f'{user.username}, у Вас уже есть портфолио!',
                'hairdresser': serialazer.data,
            }
            return Response(data)

        serialazer = CreateHairdresserSerialazer(
            data=request.data,
            user=user
        )
        if serialazer.is_valid(raise_exception=True):
            serialazer.save()
            user.is_hairdresser = True
            user.save()
            data = {'successful': 'Портфолио успешно создано!'}
            return Response(data, status=status.HTTP_200_OK)
