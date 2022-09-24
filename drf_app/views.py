from django.contrib.auth.models import User
from rest_framework import status, generics
from rest_framework.generics import UpdateAPIView
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
                                MAX_COUNT,
                                delete_avatar_directory)
from .permissons import IsOwner, IsHairdresserOwner
from .serialazers import (CreateUserSerializer,
                          UpdateUserSerializer,
                          SimpleUserSerializer,
                          GetHairdresserSerializer,
                          CreateHairdresserSerializer,
                          UpdateHairdresserSerializer,
                          SkillSerializer,
                          RegionSerializer,
                          CityWithIDSerializer,
                          GetHairdresserCommentsSerializer,
                          CreateCommentSerializer,
                          PhotoSerializer,
                          ChangePasswordSerializer, )
from .services import (convert_and_save_photo_to_portfolio,
                       get_photo_urls,
                       check_comments_count,
                       convert_and_save_avatar,
                       set_default_avatar)


class CreateUserAPIView(APIView):
    """ Регистрация пользователя """

    def post(self, request):
        if request.user.is_authenticated:
            return Response(
                {'error': 'Выйдите из аккаунта, чтобы создать нового пользователя.'},
                status=status.HTTP_403_FORBIDDEN
            )
        serializer = CreateUserSerializer(data=request.data)
        data = {}
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            username = serializer.validated_data.get('username')
            data['successful'] = f'Пользователь {username} успешно зарегистрирован!'
            return Response(data, status=status.HTTP_201_CREATED)
        else:
            data = serializer.errors
            return Response(data)


class AddAvatarAPIView(APIView):
    """ Загрузить аватар """

    permission_classes = (
        IsAuthenticated,
        IsOwner
    )

    def post(self, request):
        user = SimpleUser.objects.get(slug=request.user.simpleuser.slug)
        self.check_object_permissions(
            request=request,
            obj=user
        )
        image = request.data.get('avatar')
        if not image:
            return Response(
                {'error': 'Не передано фото для загрузки!'},
                status=status.HTTP_400_BAD_REQUEST
            )
        if not isinstance(image, str):
            return Response(
                {'error': 'Не выполнено! Ожидается тип данных - строка.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        errors = convert_and_save_avatar(
            image=image,
            user=user
        )
        if errors:
            return Response(
                {
                    'error': 'Фото не загружено!',
                    'info': f'{errors.get("message")} Количество файлов - {errors.get("count")}'
                },
                status=status.HTTP_201_CREATED
            )
        else:
            return Response(
                {'successful': 'Фото успешно загружено!'},
                status=status.HTTP_201_CREATED
            )


class DeleteAvatarAPIView(APIView):
    """ Удаление аватара """

    permission_classes = (
        IsAuthenticated,
        IsOwner
    )

    def delete(self, request):
        user = SimpleUser.objects.get(slug=request.user.simpleuser.slug)
        if user.default_avatar:
            return Response(
                {'error': 'У Вас установлен стандартный аватар!'},
                status=status.HTTP_400_BAD_REQUEST
            )
        self.check_object_permissions(
            request=request,
            obj=user
        )
        delete_avatar_directory(person_slug=user.slug)
        set_default_avatar(user=user)

        return Response({'successful': 'Фото успешно удалено!'})


class ChangePasswordView(UpdateAPIView):
    """ Изменение пароля """

    serializer_class = ChangePasswordSerializer
    model = User
    permission_classes = (IsAuthenticated,)

    def get_object(self, queryset=None):
        return self.request.user

    def update(self, request, *args, **kwargs):
        self.user = self.get_object()
        serializer = self.get_serializer(data=request.data)

        if serializer.is_valid():
            # Check old password
            if not self.user.check_password(serializer.data.get("old_password")):
                return Response(
                    {'error': 'Неверный пароль!'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            # set_password also hashes the password that the user will get
            self.user.set_password(serializer.data.get("new_password"))
            self.user.save()
            return Response(
                {'successful': 'Пароль успешно изменен!'},
                status=status.HTTP_200_OK
            )

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )


class UpdateDeleteUserAPIView(APIView):
    """ Изменение и удаление данных пользователя """

    permission_classes = (
        IsAuthenticated,
        IsOwner,
    )

    def get(self, request):
        username = request.user.username
        user = User.objects.filter(username=username).first()
        self.check_object_permissions(
            request=request,
            obj=user
        )
        data = SimpleUserSerializer(user.simpleuser)
        return Response(data.data)

    def put(self, request):
        username = request.user.username
        user = User.objects.filter(username=username).first()
        self.check_object_permissions(
            request=request,
            obj=user
        )
        serializer = UpdateUserSerializer(
            data=request.data,
            instance=user
        )
        serializer.is_valid(raise_exception=True)
        if 'first_name' not in serializer.validated_data and 'last_name' not in serializer.validated_data:
            data = {
                'error': 'Передайте значения параметров first_name и/или last_name'
            }
            return Response(data, status=status.HTTP_400_BAD_REQUEST)

        serializer.save()
        data = {'successful': 'first_name и/или last_name успешно изменены!'}
        return Response(data, status=status.HTTP_200_OK)

    def delete(self, request):
        username = request.user.username
        user = User.objects.filter(username=username).first()
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
            serializer = GetHairdresserSerializer(hairdresser)
            data = {
                'info': f'{user.username}, у Вас уже есть портфолио!',
                'hairdresser': serializer.data,
            }
            return Response(data, status=status.HTTP_400_BAD_REQUEST)

        serializer = CreateHairdresserSerializer(
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

    def post(self, request):
        username = request.user.username
        hairdresser = Hairdresser.objects.filter(owner__username=username).first()
        if not hairdresser:
            return Response(
                {'error': 'У вас нет портфолио парикмахера.'},
                status=status.HTTP_404_NOT_FOUND
            )
        self.check_object_permissions(
            request=request,
            obj=hairdresser
        )
        images = request.data.get('images')
        if not isinstance(images, list):
            return Response(
                {'error': 'Не выполнено! Ожидается список файлов.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        if len(images) == 0:
            return Response(
                {'error': 'Передан пустой список.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        elif len(images) > MAX_COUNT:
            return Response(
                {'error': f'Лимит загрузки - {MAX_COUNT} файлов за один раз!'},
                status=status.HTTP_400_BAD_REQUEST
            )
        errors = convert_and_save_photo_to_portfolio(
            images=images,
            username=username
        )
        if errors:
            return Response(
                {
                    'warning': 'Не все фото были загружены!',
                    'info': f'{errors.get("message")} Количество файлов - {errors.get("count")}'
                },
                status=status.HTTP_201_CREATED
            )
        else:
            return Response(
                {'successful': 'Фото успешно загружены!'},
                status=status.HTTP_201_CREATED
            )


class RemovePhotoFromPortfolio(APIView):
    """ Удаление всех фото в портфолио """

    permission_classes = (
        IsAuthenticated,
        IsHairdresserOwner,
    )

    def delete(self, request):
        username = request.user.username
        hairdresser = Hairdresser.objects.filter(owner__username=username).first()
        if not hairdresser:
            return Response(
                {'error': 'У вас нет портфолио парикмахера.'},
                status=status.HTTP_404_NOT_FOUND
            )
        self.check_object_permissions(
            request=request,
            obj=hairdresser
        )
        delete_portfolio_directory(person_slug=username)
        return Response(
            {'successful': 'Фото успешно удалены!'}
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
        serializer = GetHairdresserSerializer(hairdresser)
        data = {
            'hairdresser': serializer.data
        }
        # Получаем словарь со списком ссылок на фото в портфолио
        portfolio_urls = get_photo_urls(username=owner)
        if portfolio_urls:
            img_serializer = PhotoSerializer(portfolio_urls)
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

    def put(self, request):
        username = request.user.username
        hairdresser = Hairdresser.objects.filter(owner__username=username).first()
        if not hairdresser:
            return Response(
                {'error': 'У вас нет портфолио парикмахера.'},
                status=status.HTTP_404_NOT_FOUND
            )
        if not request.data:
            return Response(
                {'error': 'Данные для изменения не переданы.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        self.check_object_permissions(
            request=request,
            obj=hairdresser
        )
        serializer = UpdateHairdresserSerializer(
            instance=hairdresser,
            data=request.data,
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        data = {'successful': 'Данные успешно изменены!'}
        return Response(data, status=status.HTTP_200_OK)

    def delete(self, request):
        username = request.user.username
        simple_user = SimpleUser.objects.filter(owner__username=username).first()
        if not simple_user:
            return Response(
                {'error': f'У вас нет портфолио парикмахера.'},
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
    serializer_class = SkillSerializer


class RegionsAPIView(generics.ListAPIView):
    """ Просмотр всех областей """

    queryset = Region.objects.all().order_by('pk')
    serializer_class = RegionSerializer


class CitiesAPIView(generics.ListAPIView):
    """ Просмотр всех городов """

    queryset = City.objects.all().order_by('region')
    serializer_class = CityWithIDSerializer


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
        serializer = CityWithIDSerializer(city, many=True)
        return Response(serializer.data)


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
        serializer = CityWithIDSerializer(cities, many=True)
        return Response(serializer.data)


class SelectionAPIView(APIView):
    """ Подбор парикмахеров по критериям """

    def get(self, request):
        city = request.data.get('city')
        if city:
            if not isinstance(city, (int, str)):
                return Response(
                    {'error': 'Передан неверный тип данных!'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        skills = request.data.get('skills')
        if skills:
            if not isinstance(skills, (list, tuple)):
                return Response(
                    {'error': 'Передан неверный тип данных!'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        skills_list = [skill for skill in skills] if skills else []
        if not city and not skills_list:
            return Response(
                {'error': 'Не переданы критерии поиска!'},
                status=status.HTTP_400_BAD_REQUEST
            )
        result = get_selection_by_filters(
            model=Hairdresser,
            context={},
            city=city,
            skills=skills_list,
        )
        serializer = GetHairdresserSerializer(
            result.get('hairdresser'),
            many=True
        )
        if not serializer.data:
            return Response(
                {'info': 'По Вашему запросу результаты не найдены.'}
            )

        # добавляем к общим данных фото в портфолио, если они есть
        data = {}
        for hairdresser in serializer.data:
            owner = hairdresser.get('owner')
            data[owner] = hairdresser
            portfolio_urls = get_photo_urls(username=owner)
            if portfolio_urls:
                img_serializer = PhotoSerializer(portfolio_urls)
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

    def get(self, request):
        username = request.data.get('username')
        if not username:
            return Response(
                {'error': 'Не передан username!'},
                status=status.HTTP_400_BAD_REQUEST
            )
        user = SimpleUser.objects.filter(username=username)
        if not user:
            return Response(
                {'error': f'Пользователь "{username}" не найден!'},
                status=status.HTTP_404_NOT_FOUND
            )
        comments = Comment.objects.filter(
            belong_to__owner__username=username
        )
        serializer = GetHairdresserCommentsSerializer(
            comments,
            many=True
        )
        return Response(serializer.data)


class AddCommentAPIview(APIView):
    """ Добавить отзыв """

    permission_classes = (
        IsAuthenticated,
    )

    def post(self, request):
        belong_to = request.data.get('belong_to')
        if not belong_to:
            return Response(
                {'error': 'Не передан параметр "belong_to"!'},
                status=status.HTTP_400_BAD_REQUEST
            )
        who_do_we_evaluate = (SimpleUser.objects
                              .filter(slug=belong_to)
                              .first())
        if not who_do_we_evaluate:
            return Response(
                {'error': f'Парикмахер не найден!'},
                status=status.HTTP_404_NOT_FOUND
            )
        who_evaluates = SimpleUser.objects.get(
            slug=request.user.simpleuser.slug
        )

        if who_evaluates.slug == who_do_we_evaluate.slug:
            return Response(
                {'error': 'Неверные данные!'},
                status=status.HTTP_403_FORBIDDEN
            )
        # защита от спама
        if check_comments_count(who_evaluates, who_do_we_evaluate):
            return Response(
                {'error': f'На сегодня превышен лимит отзывов к пользователю '
                          f'{who_do_we_evaluate.username}!'},
                status=status.HTTP_403_FORBIDDEN
            )

        serializer = CreateCommentSerializer(
            data=request.data,
            author=who_evaluates,
            belong_to=who_do_we_evaluate
        )
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(
                {'successful': 'Отзыв успешно добавлен!'},
                status=status.HTTP_201_CREATED
            )
