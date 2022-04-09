# Generated by Django 4.0.3 on 2022-04-09 14:52

from django.db import migrations, models
import django.db.models.deletion
import phonenumber_field.modelfields
import users_app.models


class Migration(migrations.Migration):

    dependencies = [
        ('users_app', '0002_alter_hairdresser_city_alter_hairdresser_skills_and_more'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='city',
            options={'verbose_name': 'город', 'verbose_name_plural': 'города'},
        ),
        migrations.AlterModelOptions(
            name='hairdresser',
            options={'verbose_name': 'парикмахер', 'verbose_name_plural': 'парикмахеры'},
        ),
        migrations.AlterModelOptions(
            name='simpleuser',
            options={'verbose_name': 'простого пользователя', 'verbose_name_plural': 'простые пользователи'},
        ),
        migrations.AlterModelOptions(
            name='skill',
            options={'verbose_name': 'навык', 'verbose_name_plural': 'навыки'},
        ),
        migrations.AlterField(
            model_name='hairdresser',
            name='phone',
            field=phonenumber_field.modelfields.PhoneNumberField(max_length=128, region=None, verbose_name='номер телефона'),
        ),
        migrations.AlterField(
            model_name='hairdresser',
            name='portfolio',
            field=models.ImageField(blank=True, upload_to=users_app.models.path_to_user_portfolio_directory, verbose_name='портфолио'),
        ),
        migrations.AlterField(
            model_name='simpleuser',
            name='avatar',
            field=models.ImageField(blank=True, upload_to=users_app.models.path_to_user_avatar_directory, verbose_name='фото профиля'),
        ),
        migrations.CreateModel(
            name='Comment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('autor', models.CharField(max_length=50, verbose_name='автор')),
                ('text', models.TextField(max_length=3000, verbose_name='текст комментария')),
                ('rating_value', models.ImageField(upload_to='', verbose_name='добавить рейтинг')),
                ('date_added', models.DateTimeField(auto_now_add=True)),
                ('belong_to', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='users_app.hairdresser', verbose_name='кому')),
            ],
            options={
                'verbose_name': 'комментарий',
                'verbose_name_plural': 'комментарии',
            },
        ),
    ]
