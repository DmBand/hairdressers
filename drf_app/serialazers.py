from django.contrib.auth.models import User
from django.core.validators import RegexValidator
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from users_app.models import (City,
                              SimpleUser,
                              Skill,
                              Hairdresser,
                              Region, )
from users_app.services import create_new_user, create_new_hairdresser
from selection_app.models import Comment
from selection_app.services import create_new_comment


class CreateUserSerializer(serializers.Serializer):
    """ Регистрация пользователя """

    username_validator = RegexValidator(
        regex=r'^[0-9a-zA-Z_-]*$',
        message='Допускаются буквы a-zA-Z, цифры и символы _- (не более 30).',
    )
    first_and_last_name_validator = RegexValidator(
        regex=r'^[a-zA-Zа-яёА-ЯЁ-]*$',
        message='Допускаются буквы а-яА-Я, a-zA-Z.'
    )
    password_validator = RegexValidator(
        regex=r'^[^а-яёА-ЯЁ]+$',
        message='Символы кириллицы (а-яА-Я) не допускаются.'
    )

    username = serializers.CharField(
        label='Логин',
        max_length=30,
        validators=[username_validator],
    )
    first_name = serializers.CharField(
        label='Имя',
        validators=[first_and_last_name_validator],
    )
    last_name = serializers.CharField(
        label='Фамилия',
        validators=[first_and_last_name_validator],
    )
    email = serializers.EmailField(
        label='Эл. адрес',
    )
    password1 = serializers.CharField(
        label='Пароль',
        validators=[password_validator],
    )
    password2 = serializers.CharField(
        label='Повторите пароль',
    )

    def create(self, validated_data):
        username = validated_data.get('username')
        if User.objects.filter(username__iexact=username).exists():
            raise serializers.ValidationError({'detail': f'Логин {username} уже используется!'})

        email = validated_data.get('email')
        if User.objects.filter(email__iexact=email).exists():
            raise serializers.ValidationError({'detail': 'Пользователь с таким эл. адресом уже существует!'})

        password1 = validated_data.get('password1')
        password2 = validated_data.get('password2')
        if password1 != password2:
            raise serializers.ValidationError({'detail': "Пароли не совпадают!"})

        user = User.objects.create_user(
            username=validated_data.get('username'),
            first_name=validated_data.get('first_name'),
            last_name=validated_data.get('last_name'),
            email=email,
            password=password1,
        )

        simple_user = create_new_user(user=user)
        return simple_user


class UpdateUserSerializer(serializers.Serializer):
    """ Изменение или удаление пользователя """

    first_and_last_name_validator = RegexValidator(
        regex=r'^[a-zA-Zа-яёА-ЯЁ-]*$',
        message='Допускаются буквы а-яА-Я, a-zA-Z.'
    )
    first_name = serializers.CharField(
        label='Имя',
        validators=[first_and_last_name_validator],
        required=False
    )
    last_name = serializers.CharField(
        label='Фамилия',
        validators=[first_and_last_name_validator],
        required=False
    )

    def update(self, instance, validated_data):
        simple_user = SimpleUser.objects.get(username=instance.username)
        first_name = validated_data.get('first_name')
        last_name = validated_data.get('last_name')
        if first_name:
            instance.first_name = first_name.title()
            simple_user.name = first_name.title()
            instance.save()
            simple_user.save()
        if last_name:
            instance.last_name = last_name.title()
            simple_user.surname = last_name.title()
            instance.save()
            simple_user.save()

        return instance


class SimpleUserSerializer(serializers.ModelSerializer):
    """ Простой пользователь """

    owner = serializers.SlugRelatedField(
        slug_field='username',
        read_only=True,
    )

    class Meta:
        model = SimpleUser
        fields = (
            'owner',
            'username',
            'name',
            'surname',
            'email',
            'slug',
            'is_hairdresser',
            'date_of_registration',
        )


class RegionSerializer(serializers.ModelSerializer):
    """ Области """

    class Meta:
        model = Region
        fields = '__all__'


class CityWithIDSerializer(serializers.ModelSerializer):
    """ Город со всеми полями """

    region = serializers.SlugRelatedField(
        slug_field='name',
        read_only=True,
    )

    class Meta:
        model = City
        fields = '__all__'


class CityWithoutIDSerializer(serializers.ModelSerializer):
    """ Город без поля ID """

    region = serializers.SlugRelatedField(
        slug_field='name',
        read_only=True,
    )

    class Meta:
        model = City
        exclude = (
            'id',
        )


class SkillSerializer(serializers.ModelSerializer):
    """ Навыки """

    class Meta:
        model = Skill
        fields = '__all__'


class PhotoSerializer(serializers.Serializer):
    """ Ссылки на фото в портфолио """

    urls = serializers.ListField()


class GetHairdresserSerializer(serializers.ModelSerializer):
    """ Парикмахер """

    owner = serializers.SlugRelatedField(
        slug_field='username',
        read_only=True,
    )
    city = CityWithoutIDSerializer()
    skills = serializers.SlugRelatedField(
        slug_field='name',
        read_only=True,
        many=True
    )

    class Meta:
        model = Hairdresser
        exclude = (
            'id',
            'portfolio',
        )


class GetHairdresserOnlyUsernameSerializer(serializers.ModelSerializer):
    """ Никнейм парикмахера """

    owner = serializers.SlugRelatedField(
        slug_field='username',
        read_only=True,
    )

    class Meta:
        model = Hairdresser
        fields = (
            'owner',
        )


class CreateHairdresserSerializer(serializers.ModelSerializer):
    """ Создать парикмахера """

    def __init__(self, data, **kwargs):
        super().__init__(data=data)
        self.user = kwargs.get('user')

    class Meta:
        model = Hairdresser
        fields = (
            'city',
            'phone',
            'skills',
            'instagram',
            'another_info',
        )

    def create(self, validated_data):
        hairdresser = create_new_hairdresser(
            user=self.user,
            data=validated_data,
        )
        return hairdresser


class UpdateHairdresserSerializer(serializers.ModelSerializer):
    """ Обновить портфолио парикмахера """

    class Meta:
        model = Hairdresser
        fields = (
            'city',
            'phone',
            'skills',
            'instagram',
            'another_info',
        )

    def is_valid(self, raise_exception=False):
        city = self.initial_data.get('city')
        phone = self.initial_data.get('phone')
        skills = self.initial_data.get('skills')
        if not city:
            self.initial_data['city'] = self.instance.city.id
        if not phone:
            self.initial_data['phone'] = str(self.instance.phone)
        if not skills:
            current_skills = [skill.id for skill in self.instance.skills.all()]
            self.initial_data['skills'] = current_skills
        super().is_valid(raise_exception=raise_exception)

    def update(self, instance, validated_data):
        instance.city = validated_data.get('city', instance.city)
        instance.phone = validated_data.get('phone', instance.phone)
        instance.instagram = validated_data.get('instagram', instance.instagram)
        instance.another_info = validated_data.get('another_info', instance.another_info)
        all_skills = validated_data.get('skills')
        current_skills = instance.skills.all()
        if all_skills:
            for skill in current_skills:
                instance.skills.remove(skill.id)
            instance.skills.add(*all_skills)
        instance.save()
        return instance


class GetHairdresserCommentsSerializer(serializers.ModelSerializer):
    """ Отзывы о парикмахере """

    belong_to = GetHairdresserOnlyUsernameSerializer()

    class Meta:
        model = Comment
        exclude = ('id',)


class CreateCommentSerializer(serializers.ModelSerializer):
    """ Добавить отзыв """

    def __init__(self, data, **kwargs):
        super().__init__(data=data)
        self.author = kwargs.get('author')
        self.belong_to = kwargs.get('belong_to')

    class Meta:
        model = Comment
        fields = (
            'text',
            'rating_value',
        )

    def create(self, validated_data):
        comment = create_new_comment(
            author=self.author,
            belong_to=self.belong_to,
            data=validated_data
        )
        return comment

    def is_valid(self, raise_exception=False):
        super().is_valid()
        text = self.validated_data.get('text')
        if len(text) < 10:
            raise ValidationError(
                {'error': 'Текст комментария должен содержать не менее 10 символов!'}
            )
        rating = self.validated_data.get('rating_value')
        if rating < 0 or rating > 5:
            raise ValidationError(
                {'error': 'Рейтинг должен быть от 0 до 5 включительно!'}
            )
        return text, rating
