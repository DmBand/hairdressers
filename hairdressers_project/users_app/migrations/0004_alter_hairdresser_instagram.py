# Generated by Django 4.0.3 on 2022-05-06 10:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users_app', '0003_alter_city_options_simpleuser_default_avatar_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='hairdresser',
            name='instagram',
            field=models.CharField(blank=True, max_length=100, verbose_name='инстаграм'),
        ),
    ]
