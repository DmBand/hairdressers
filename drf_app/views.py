import base64

from django.contrib.auth.models import User
from rest_framework import status, generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from selection_app.models import Comment
from selection_app.services import get_selection_by_filters
from users_app.models import (Hairdresser,
                              SimpleUser,
                              Skill,
                              City,
                              Region, )
from users_app.services import check_number_of_files_in_portfolio
from .permissons import IsOwner, IsHairdresserOwner
from .serialazers import (CreateUserSerialazer,
                          UpdateUserSerialazer,
                          SimpleUserSerialazer,
                          GetHairdresserSerialazer,
                          CreateHairdresserSerialazer,
                          UpdateHairdresserSerialazer,
                          SkillSerialazer,
                          RegionSerialazer,
                          CityWithIDSerialazer,
                          GetHairdresserCommentsSerialazer,
                          CreateCommentSerialazer, )
from .services import get_images
# TODO ЗАГРУЗКА ФОТО!
# TODO CSRF TOKEN!
# TODO Загрузка "битых" фото
# TODO закрытие изображений после сжатия


class CreateUserAPIView(APIView):
    """ Регистрация пользователя """

    def post(self, request, **kwargs):
        serialazer = CreateUserSerialazer(data=request.data)
        data = {}
        if serialazer.is_valid(raise_exception=True):
            serialazer.save()
            username = serialazer.validated_data.get('username')
            data['successful'] = f'Пользователь {username} успешно зарегестрирован!'
            return Response(data, status=status.HTTP_201_CREATED)
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
            return Response(
                {'error': f'Пользователь {username} не найден'},
                status=status.HTTP_404_NOT_FOUND
            )

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
            return Response(
                {'error': f'Пользователь {username} не найден'},
                status=status.HTTP_404_NOT_FOUND
            )

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
        data = {'successful': 'first_name и/или last_name успешно изменены!'}
        return Response(data, status=status.HTTP_200_OK)

    def delete(self, request, **kwargs):
        username = kwargs.get('username')
        user = User.objects.filter(username=username).first()
        if not user:
            return Response(
                {'error': f'Пользователь {username} не найден'},
                status=status.HTTP_404_NOT_FOUND
            )

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
            return Response(data, status=status.HTTP_201_CREATED)


class AddPhotoToPortfolioAPIView(APIView):
    """ Добавить фото в портфолио """

    permission_classes = (
        IsAuthenticated,
        IsHairdresserOwner
    )

    def post(self, request, **kwargs):
        username = kwargs.get('username')
        hairdresser = Hairdresser.objects.filter(owner__username=username).first()
        if not hairdresser:
            return Response(
                {'error': f'Портфолио не найдено. Проверьте username пользователя.'},
                status=status.HTTP_404_NOT_FOUND
            )
        self.check_object_permissions(
            request=request,
            obj=hairdresser
        )
        images = request.data.get('images')
        get_images(
            images=images,
            username=username
        )
        return Response(
            {'message': 'successful'}
        )


class GetHairdresserAPIView(APIView):
    """ Просмотр портфолио парикмахера """

    def get(self, request, **kwargs):
        owner = kwargs.get('username')
        hairdresser = Hairdresser.objects.filter(owner__username=owner).first()
        if not hairdresser:
            return Response(
                {'error': f'Портфолио не найдено! Проверьте username пользователя.'},
                status=status.HTTP_404_NOT_FOUND
            )
        serialazer = GetHairdresserSerialazer(hairdresser)
        return Response(serialazer.data, status=status.HTTP_200_OK)


class UpdateDeleteHairdresserAPIView(APIView):
    """ Изменение и удаление портфолио парикмахера """

    permission_classes = (
        IsAuthenticated,
        IsHairdresserOwner,
    )

    def put(self, request, **kwargs):
        username = kwargs.get('username')
        hairdresser = Hairdresser.objects.filter(owner__username=username).first()
        if not hairdresser:
            return Response(
                {'error': f'Портфолио не найдено. Проверьте username пользователя.'},
                status=status.HTTP_404_NOT_FOUND
            )
        if not request.data:
            return Response(
                {'message': 'Данные не переданы'},
                status=status.HTTP_200_OK
            )
        self.check_object_permissions(
            request=request,
            obj=hairdresser
        )
        serialazer = UpdateHairdresserSerialazer(
            instance=hairdresser,
            data=request.data,
        )
        serialazer.is_valid(raise_exception=True)
        serialazer.save()
        data = {'successful': 'Данные успешно изменены!'}
        return Response(data, status=status.HTTP_200_OK)

    def delete(self, request, **kwargs):
        username = kwargs.get('username')
        simple_user = SimpleUser.objects.filter(owner__username=username).first()
        if not simple_user:
            return Response(
                {'error': f'Портфолио не найдено. Проверьте имя пользователя'},
                status=status.HTTP_404_NOT_FOUND
            )
        self.check_object_permissions(
            request=request,
            obj=simple_user.hairdresser
        )
        simple_user.hairdresser.delete()
        simple_user.is_hairdresser = False
        simple_user.save()
        data = {'successful': f'Портфолио пользователя {username} успешно удалено!'}
        return Response(data, status=status.HTTP_200_OK)


class SkillsAPIView(generics.ListAPIView):
    """ Просмотр доступных навыков """

    queryset = Skill.objects.all().order_by('id')
    serializer_class = SkillSerialazer


class RegionsAPIView(generics.ListAPIView):
    """ Просмотр всех областей """

    queryset = Region.objects.all().order_by('pk')
    serializer_class = RegionSerialazer


class CitiesAPIView(generics.ListAPIView):
    """ Просмотр всех городов """

    queryset = City.objects.all().order_by('region')
    serializer_class = CityWithIDSerialazer


class GetCityAPIView(APIView):
    """ Просмотр конкретного города """

    def get(self, request, **kwargs):
        pk = kwargs.get('pk')
        city = City.objects.filter(pk=pk)
        if not city:
            return Response(
                {'error': 'Город не найден!'},
                status=status.HTTP_404_NOT_FOUND
            )
        serialazer = CityWithIDSerialazer(city, many=True)
        return Response(serialazer.data)


class GetAllCitiesInTheRegion(APIView):
    """ Просмотр всех городов одной области """

    def get(self, request, **kwargs):
        pk = kwargs.get('pk')
        cities = City.objects.filter(region__pk=pk)
        if not cities:
            return Response(
                {'error': 'Города не найдены! Проверьте правильность передаваемых данных.'},
                status=status.HTTP_404_NOT_FOUND
            )
        serialazer = CityWithIDSerialazer(cities, many=True)
        return Response(serialazer.data)


class SelectionAPIView(APIView):
    """ Подбор парикмахеров по критериям """

    def get(self, request):
        city = request.data.get('city')
        skills = request.data.get('skill')
        skills_list = [skill for skill in skills] if skills else []
        if not city and not skills_list:
            return Response(
                {'error': 'Не переданы критерии поиска!'},
                status=status.HTTP_404_NOT_FOUND
            )
        result = get_selection_by_filters(
            model=Hairdresser,
            context={},
            city=city,
            skills=skills_list,
        )
        serialazer = GetHairdresserSerialazer(
            result.get('hairdresser'),
            many=True
        )
        if not serialazer.data:
            return Response(
                {'error': 'По Вашему запросу результаты не найдены'}
            )
        return Response(
            serialazer.data,
            status=status.HTTP_200_OK
        )


class GetCommentsAPIView(APIView):
    """ Отзывы о парикмахере """

    def get(self, request, **kwargs):
        username = kwargs.get('username')
        user = SimpleUser.objects.filter(username=username)
        if not user:
            return Response(
                {'error': f'Пользователь "{username}" не найден'},
                status=status.HTTP_404_NOT_FOUND
            )
        comments = Comment.objects.filter(
            belong_to__owner__username=username
        )
        serialazer = GetHairdresserCommentsSerialazer(
            comments,
            many=True
        )
        return Response(serialazer.data)


class AddCommentAPIview(APIView):
    """ Добавить отзыв """

    permission_classes = (
        IsAuthenticated,
    )

    def post(self, request, **kwargs):
        who_do_we_evaluate = (SimpleUser.objects
                              .filter(slug=kwargs.get('username'))
                              .first())
        if not who_do_we_evaluate:
            return Response(
                {'errpr': f'Парикмахер {kwargs.get("username")} не найден!'},
                status=status.HTTP_404_NOT_FOUND
            )
        who_evaluates = SimpleUser.objects.get(slug=request.user.simpleuser.slug)
        if who_evaluates.slug == who_do_we_evaluate.slug:
            return Response(
                {'error': 'Неверные данные!'},
                status=status.HTTP_403_FORBIDDEN
            )
        serialazer = CreateCommentSerialazer(
            data=request.data,
            autor=who_evaluates,
            belong_to=who_do_we_evaluate
        )
        if serialazer.is_valid(raise_exception=True):
            serialazer.save()
            data = {'successful': 'Отзыв успешно добавлен!'}
            return Response(data, status=status.HTTP_201_CREATED)
