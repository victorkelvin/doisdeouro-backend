from django.contrib import admin
from .models import Graduacao, Turma, Aluno, AlunoInvitation

admin.site.register(Graduacao)
admin.site.register(Turma)
admin.site.register(Aluno)
admin.site.register(AlunoInvitation)
