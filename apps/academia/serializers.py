from rest_framework import serializers
from .models import Aluno, Turma, Graduacao, DiaSemana, AlunoInvitation
import os
import base64
from django.utils import timezone

class AlunoSerializer(serializers.ModelSerializer):
    faixa = serializers.StringRelatedField(source='graduacao.faixa', read_only=True)
    turma_nome = serializers.StringRelatedField(source='turma.nome', read_only=True)
    foto_base64 = serializers.SerializerMethodField()
    
    class Meta:
        model = Aluno
        fields = '__all__'
        
    def get_foto_base64(self, obj):
        """
        Retorna a imagem em formato base64 para ser utilizada diretamente no frontend
        """
        if not obj.foto:
            return None
            
        try:
            # Pega o caminho absoluto do arquivo
            img_path = obj.foto.path
            
            # Verifica se o arquivo existe
            if not os.path.exists(img_path):
                return None
                
            # Lê o arquivo e converte para base64
            with open(img_path, "rb") as img_file:
                encoded_string = base64.b64encode(img_file.read()).decode('utf-8')
                
            # Determina o tipo de imagem
            ext = os.path.splitext(img_path)[1].lower()
            if ext == '.jpg' or ext == '.jpeg':
                mime = 'image/jpeg'
            elif ext == '.png':
                mime = 'image/png'
            else:
                mime = 'image/jpeg'  # Default
                
            # Retorna o data URL completo
            return f"data:{mime};base64,{encoded_string}"
        except Exception as e:
            print(f"Erro ao converter imagem para base64: {e}")
            return None


class TurmaSerializer(serializers.ModelSerializer):
    dias = serializers.SerializerMethodField()  

    class Meta:
        model = Turma
        fields = '__all__'

    def get_dias(self, obj):
        return [dia.dia for dia in obj.dias_da_semana.all()]



class GraduacaoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Graduacao
        fields = '__all__'

class DiaSemanaSerializer(serializers.ModelSerializer):
    class Meta:
        model = DiaSemana
        fields = ['dia']


class AlunoInvitationSerializer(serializers.ModelSerializer):
    is_valid = serializers.SerializerMethodField()
    expires_at = serializers.DateTimeField(format='%d/%m/%Y %H:%M:%S')
    
    class Meta:
        model = AlunoInvitation
        fields = ['token', 'expires_at', 'created_at', 'is_valid']
        read_only_fields = ['created_at']
    
    def get_is_valid(self, obj):
        return obj.is_valid


