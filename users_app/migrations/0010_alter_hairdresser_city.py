# Generated by Django 4.0.3 on 2022-08-14 14:14

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('users_app', '0009_alter_hairdresser_another_info_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='hairdresser',
            name='city',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='hairdresser', to='users_app.city'),
        ),
    ]