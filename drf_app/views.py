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
from users_app.services import (delete_portfolio_directory,
                                MAX_COUNT)
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
                          CreateCommentSerialazer,
                          PhotoSerialazer, )
from .services import get_images, get_photo_urls


# TODO Изменение пароля
class CreateUserAPIView(APIView):
    """ Регистрация пользователя """

    def post(self, request):
        if request.user.is_authenticated:
            return Response(
                {'detail': 'Выйдите из аккаунта, чтобы создать нового пользователя.'},
                status=status.HTTP_403_FORBIDDEN
            )
        serializer = CreateUserSerialazer(data=request.data)
        data = {}
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            username = serializer.validated_data.get('username')
            data['successful'] = f'Пользователь {username} успешно зарегистрирован!'
            return Response(data, status=status.HTTP_201_CREATED)
        else:
            data = serializer.errors
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
                {'detail': f'Пользователь {username} не найден'},
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
                {'detail': f'Пользователь {username} не найден'},
                status=status.HTTP_404_NOT_FOUND
            )

        self.check_object_permissions(
            request=request,
            obj=user
        )
        serializer = UpdateUserSerialazer(
            data=request.data,
            instance=user
        )
        serializer.is_valid(raise_exception=True)
        if 'first_name' not in serializer.validated_data and 'last_name' not in serializer.validated_data:
            data = {
                'message': 'Передайте значения параметров first_name и/или last_name'
            }
            return Response(data, status=status.HTTP_400_BAD_REQUEST)

        serializer.save()
        data = {'successful': 'first_name и/или last_name успешно изменены!'}
        return Response(data, status=status.HTTP_200_OK)

    def delete(self, request, **kwargs):
        username = kwargs.get('username')
        user = User.objects.filter(username=username).first()
        if not user:
            return Response(
                {'detail': f'Пользователь {username} не найден'},
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
            serializer = GetHairdresserSerialazer(hairdresser)
            data = {
                'detail': f'{user.username}, у Вас уже есть портфолио!',
                'hairdresser': serializer.data,
            }
            return Response(data, status=status.HTTP_400_BAD_REQUEST)

        serializer = CreateHairdresserSerialazer(
            data=request.data,
            user=user
        )
        if serializer.is_valid(raise_exception=True):
            serializer.save()
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
                {'detail': f'Портфолио не найдено. Проверьте username пользователя.'},
                status=status.HTTP_404_NOT_FOUND
            )
        self.check_object_permissions(
            request=request,
            obj=hairdresser
        )
        images = request.data.get('images')
        if not isinstance(images, list):
            return Response(
                {'detail': 'Не выполнено! Ожидается список файлов.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        if len(images) == 0:
            return Response(
                {'detail': 'Передан пустой список.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        elif len(images) > MAX_COUNT:
            return Response(
                {'detail': f'Лимит загрузки - {MAX_COUNT} файлов за один раз!'},
                status=status.HTTP_400_BAD_REQUEST
            )
        errors = get_images(
            images=images,
            username=username
        )
        if errors:
            return Response(
                {
                    'message': 'successful',
                    'errors': f'{errors.get("message")}. Количество файлов - {errors.get("count")}'
                },
                status=status.HTTP_201_CREATED
            )
        else:
            return Response(
                {'message': 'successful'},
                status=status.HTTP_201_CREATED
            )


class RemovePhotoFromPortfolio(APIView):
    """ Удаление всех фото в портфолио """

    permission_classes = (
        IsAuthenticated,
        IsHairdresserOwner,
    )

    def delete(self, request, **kwargs):
        username = kwargs.get('username')
        hairdresser = Hairdresser.objects.filter(owner__username=username).first()
        if not hairdresser:
            return Response(
                {'detail': f'Портфолио не найдено! Проверьте username пользователя.'},
                status=status.HTTP_404_NOT_FOUND
            )
        self.check_object_permissions(
            request=request,
            obj=hairdresser
        )
        delete_portfolio_directory(person_slug=username)
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
                {'detail': f'Портфолио не найдено! Проверьте username пользователя.'},
                status=status.HTTP_404_NOT_FOUND
            )
        serializer = GetHairdresserSerialazer(hairdresser)
        data = {
            'hairdresser': serializer.data
        }
        # Получаем словарь со списком ссылок на фото в портфолио
        portfolio_urls = get_photo_urls(username=owner)
        if portfolio_urls:
            img_serializer = PhotoSerialazer(portfolio_urls)
            data['portfolio'] = img_serializer.data
            data['portfolio']['count'] = len(portfolio_urls.get('urls'))
        else:
            data['portfolio'] = {'count': 0}

        return Response(data, status=status.HTTP_200_OK)


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
                {'detail': f'Портфолио не найдено. Проверьте username пользователя.'},
                status=status.HTTP_404_NOT_FOUND
            )
        if not request.data:
            return Response(
                {'message': 'Данные не переданы.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        self.check_object_permissions(
            request=request,
            obj=hairdresser
        )
        serializer = UpdateHairdresserSerialazer(
            instance=hairdresser,
            data=request.data,
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        data = {'successful': 'Данные успешно изменены!'}
        return Response(data, status=status.HTTP_200_OK)

    def delete(self, request, **kwargs):
        username = kwargs.get('username')
        simple_user = SimpleUser.objects.filter(owner__username=username).first()
        if not simple_user:
            return Response(
                {'detail': f'Портфолио не найдено. Проверьте имя пользователя'},
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
                {'detail': 'Город не найден!'},
                status=status.HTTP_404_NOT_FOUND
            )
        serializer = CityWithIDSerialazer(city, many=True)
        return Response(serializer.data)


class GetAllCitiesInTheRegion(APIView):
    """ Просмотр всех городов одной области """

    def get(self, request, **kwargs):
        pk = kwargs.get('pk')
        cities = City.objects.filter(region__pk=pk)
        if not cities:
            return Response(
                {'detail': 'Города не найдены! Проверьте правильность передаваемых данных.'},
                status=status.HTTP_404_NOT_FOUND
            )
        serializer = CityWithIDSerialazer(cities, many=True)
        return Response(serializer.data)


class SelectionAPIView(APIView):
    """ Подбор парикмахеров по критериям """

    def get(self, request):
        city = request.data.get('city')
        if city:
            if not isinstance(city, (int, str)):
                return Response(
                    {'detail': 'Передан неверный тип данных!'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        skills = request.data.get('skills')
        if skills:
            if not isinstance(skills, (list, tuple)):
                return Response(
                    {'detail': 'Передан неверный тип данных!'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        skills_list = [skill for skill in skills] if skills else []
        if not city and not skills_list:
            return Response(
                {'detail': 'Не переданы критерии поиска!'},
                status=status.HTTP_400_BAD_REQUEST
            )
        result = get_selection_by_filters(
            model=Hairdresser,
            context={},
            city=city,
            skills=skills_list,
        )
        serializer = GetHairdresserSerialazer(
            result.get('hairdresser'),
            many=True
        )
        if not serializer.data:
            return Response(
                {'detail': 'По Вашему запросу результаты не найдены'}
            )

        # добавляем к общим данных фото в портфолио, если они есть
        data = {}
        for hairdresser in serializer.data:
            owner = hairdresser.get('owner')
            data[owner] = hairdresser
            portfolio_urls = get_photo_urls(username=owner)
            if portfolio_urls:
                img_serializer = PhotoSerialazer(portfolio_urls)
                data[owner]['portfolio'] = img_serializer.data
                data[owner]['portfolio']['count'] = len(portfolio_urls.get('urls'))
            else:
                data[owner]['portfolio'] = {'count': 0}

        return Response(
            data,
            status=status.HTTP_200_OK
        )


class GetCommentsAPIView(APIView):
    """ Отзывы о парикмахере """

    def get(self, request, **kwargs):
        username = kwargs.get('username')
        user = SimpleUser.objects.filter(username=username)
        if not user:
            return Response(
                {'detail': f'Пользователь "{username}" не найден'},
                status=status.HTTP_404_NOT_FOUND
            )
        comments = Comment.objects.filter(
            belong_to__owner__username=username
        )
        serializer = GetHairdresserCommentsSerialazer(
            comments,
            many=True
        )
        return Response(serializer.data)


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
                {'detail': f'Парикмахер {kwargs.get("username")} не найден!'},
                status=status.HTTP_404_NOT_FOUND
            )
        who_evaluates = SimpleUser.objects.get(slug=request.user.simpleuser.slug)
        if who_evaluates.slug == who_do_we_evaluate.slug:
            return Response(
                {'detail': 'Неверные данные!'},
                status=status.HTTP_403_FORBIDDEN
            )
        serializer = CreateCommentSerialazer(
            data=request.data,
            autor=who_evaluates,
            belong_to=who_do_we_evaluate
        )
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            data = {'successful': 'Отзыв успешно добавлен!'}
            return Response(data, status=status.HTTP_201_CREATED)
