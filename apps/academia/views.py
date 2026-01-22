from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.pagination import PageNumberPagination
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import Aluno, Turma, Graduacao, DiaSemana, AlunoInvitation
from .serializers import (
    AlunoSerializer, GraduacaoSerializer, TurmaSerializer, 
    DiaSemanaSerializer, AlunoInvitationSerializer
)

class CustomPagination(PageNumberPagination):
    page_size = 200


class TokenPermission:
    """Verifica se um token de convite é válido"""
    def __init__(self, token):
        self.token = token
        self.is_valid = False
        self.invitation = None
        
        try:
            self.invitation = AlunoInvitation.objects.get(token=token)
            self.is_valid = self.invitation.is_valid
        except AlunoInvitation.DoesNotExist:
            pass


class AlunoViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    pagination_class = CustomPagination

    queryset = Aluno.objects.all()
    serializer_class = AlunoSerializer
    
    def get_permissions(self):
        """
        Permite que usuários sem autenticação criem alunos com um token válido
        e validem tokens de convite.
        """
        if self.action in ['create', 'validate_invitation']:
            return [AllowAny()]
        return [IsAuthenticated()]
    
    def create(self, request, *args, **kwargs):
        """
        Cria um novo aluno. Requer autenticação ou um token válido de convite.
        O token pode ser utilizado múltiplas vezes durante seu período de validade.
        """
        token = request.data.get('invitation_token')
        
        if not token:
            return Response(
                {'error': 'Token de convite é obrigatório para criar um aluno'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Verifica se o token é válido
        token_perm = TokenPermission(token)
        if not token_perm.is_valid:
            return Response(
                {'error': 'Token de convite inválido ou expirado'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Processa a criação do aluno normalmente
        return super().create(request, *args, **kwargs)
    
    @action(detail=False, methods=['post'], permission_classes=[IsAuthenticated])
    def generate_invitation(self, request):
        """
        Gera um novo token de convite temporário para criar um aluno.
        
        Query params:
            hours: Número de horas até a expiração (padrão: 24)
        """
        hours = int(request.query_params.get('hours', 24))
        
        if hours <= 0:
            return Response(
                {'error': 'hours deve ser um número positivo'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        invitation = AlunoInvitation.create_invitation(hours=hours)
        serializer = AlunoInvitationSerializer(invitation)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    @action(detail=False, methods=['get'], permission_classes=[AllowAny])
    def validate_invitation(self, request):
        """
        Valida um token de convite sem utilizá-lo.
        
        Query params:
            token: O token a validar
        """
        token = request.query_params.get('token')
        
        if not token:
            return Response(
                {'error': 'Token é obrigatório'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        token_perm = TokenPermission(token)
        
        if token_perm.invitation:
            serializer = AlunoInvitationSerializer(token_perm.invitation)
            return Response(serializer.data)
        
        return Response(
            {'error': 'Token não encontrado'},
            status=status.HTTP_404_NOT_FOUND
        )


class GraduacaoViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]

    queryset = Graduacao.objects.all().order_by('id')
    serializer_class = GraduacaoSerializer

class TurmaViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]

    queryset = Turma.objects.all().order_by('nome')
    serializer_class = TurmaSerializer

class DiaSemanaViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]

    queryset = DiaSemana.objects.all()
    serializer_class = DiaSemanaSerializer

