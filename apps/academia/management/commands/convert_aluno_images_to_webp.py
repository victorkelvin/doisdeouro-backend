from django.core.management.base import BaseCommand
from apps.academia.models import Aluno
from django.conf import settings
from PIL import Image
import os

class Command(BaseCommand):
    help = 'Converte todas as fotos de alunos para o formato WebP.'

    def handle(self, *args, **options):
        alunos = Aluno.objects.exclude(foto='')
        total = alunos.count()
        convertidos = 0
        for aluno in alunos:
            if not aluno.foto:
                continue
            original_path = aluno.foto.path
            if not os.path.exists(original_path):
                self.stdout.write(self.style.WARNING(f'Arquivo não encontrado: {original_path}'))
                continue
            # Novo caminho com extensão .webp
            base, _ = os.path.splitext(original_path)
            webp_path = base + '.webp'
            try:
                with Image.open(original_path) as img:
                    img.save(webp_path, 'WEBP', quality=85)
                # Atualiza o campo foto para o novo arquivo
                relative_webp = aluno.foto.name.rsplit('.', 1)[0] + '.webp'
                aluno.foto.name = relative_webp
                aluno.save(update_fields=['foto'])
                # Remove o arquivo original (opcional)
                if os.path.exists(original_path) and original_path != webp_path:
                    os.remove(original_path)
                convertidos += 1
                self.stdout.write(self.style.SUCCESS(f'Convertido: {aluno.nome} -> {webp_path}'))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'Erro ao converter {original_path}: {e}'))
        self.stdout.write(self.style.SUCCESS(f'Conversão concluída: {convertidos}/{total} imagens convertidas.'))
