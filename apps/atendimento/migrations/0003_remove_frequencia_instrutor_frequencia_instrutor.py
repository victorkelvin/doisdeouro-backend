# Generated by Django 4.2.7 on 2025-03-31 19:10

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('atendimento', '0002_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='frequencia',
            name='instrutor',
        ),
        migrations.AddField(
            model_name='frequencia',
            name='instrutor',
            field=models.ManyToManyField(to=settings.AUTH_USER_MODEL),
        ),
    ]
