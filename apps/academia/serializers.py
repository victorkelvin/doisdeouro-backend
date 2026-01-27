from rest_framework import serializers
from .models import Aluno, Turma, Graduacao, DiaSemana, AlunoInvitation

class AlunoSerializer(serializers.ModelSerializer):
    faixa = serializers.StringRelatedField(source='graduacao.faixa', read_only=True)
    turma_nome = serializers.StringRelatedField(source='turma.nome', read_only=True)

    class Meta:
        model = Aluno
        fields = '__all__'


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


