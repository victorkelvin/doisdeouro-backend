# Generated by Django 4.2.7 on 2025-04-07 20:41

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('academia', '0007_alter_aluno_contato_alter_aluno_email_and_more'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('atendimento', '0003_remove_frequencia_instrutor_frequencia_instrutor'),
    ]

    operations = [
        migrations.CreateModel(
            name='Aula',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('data', models.DateTimeField(default=django.utils.timezone.now, verbose_name='Data')),
                ('horario_inicio', models.TimeField(verbose_name='Horário de Início')),
                ('horario_fim', models.TimeField(verbose_name='Horário de Fim')),
                ('observacao', models.TextField(blank=True, null=True, verbose_name='Observação')),
                ('aluno_presente', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='academia.aluno', verbose_name='Aluno Presente')),
                ('instrutor', models.ManyToManyField(to=settings.AUTH_USER_MODEL)),
                ('turma', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='academia.turma', verbose_name='Turma')),
            ],
            options={
                'verbose_name': 'Frequência',
                'verbose_name_plural': 'Frequências',
                'unique_together': {('data', 'aluno_presente', 'turma')},
            },
        ),
        migrations.DeleteModel(
            name='Frequencia',
        ),
    ]
