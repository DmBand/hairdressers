# Generated by Django 4.0.3 on 2022-05-10 13:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users_app', '0004_alter_hairdresser_instagram'),
    ]

    operations = [
        migrations.AlterField(
            model_name='skill',
            name='name',
            field=models.CharField(db_index=True, max_length=80, verbose_name='навык'),
        ),
    ]
