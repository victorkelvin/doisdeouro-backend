# Generated by Django 4.2.7 on 2025-03-28 16:57

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('academia', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='turma',
            name='Instrutor',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='Instrutor'),
        ),
        migrations.AddField(
            model_name='aluno',
            name='graduacao',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='academia.graduacao', verbose_name='Graduação'),
        ),
        migrations.AddField(
            model_name='aluno',
            name='turma',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='academia.turma', verbose_name='Turma'),
        ),
    ]
