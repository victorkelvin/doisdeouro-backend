from django.test import TestCase
from django.utils import timezone
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from datetime import timedelta
import json

from .models import Graduacao, DiaSemana, Turma, Aluno, AlunoInvitation
from .serializers import (
    AlunoSerializer, GraduacaoSerializer, TurmaSerializer, 
    DiaSemanaSerializer, AlunoInvitationSerializer
)
from apps.contas.models import Instrutor


# ============================================================================
# MODELS TESTS
# ============================================================================

class GraduacaoModelTest(TestCase):
    """Tests for Graduacao model"""
    
    def setUp(self):
        self.graduacao = Graduacao.objects.create(faixa='Branca')
    
    def test_graduacao_creation(self):
        """Test creating a Graduacao instance"""
        self.assertEqual(self.graduacao.faixa, 'Branca')
        self.assertTrue(isinstance(self.graduacao, Graduacao))
    
    def test_graduacao_str(self):
        """Test string representation of Graduacao"""
        self.assertEqual(str(self.graduacao), 'Branca')
    
    def test_graduacao_unique_constraint(self):
        """Test that faixa field is unique"""
        with self.assertRaises(Exception):
            Graduacao.objects.create(faixa='Branca')
    
    def test_graduacao_ordering(self):
        """Test that Graduacao is ordered by faixa"""
        Graduacao.objects.create(faixa='Preta')
        Graduacao.objects.create(faixa='Amarela')
        
        graduacoes = Graduacao.objects.all()
        self.assertEqual(graduacoes[0].faixa, 'Amarela')
        self.assertEqual(graduacoes[1].faixa, 'Branca')
        self.assertEqual(graduacoes[2].faixa, 'Preta')


class DiaSemanaModelTest(TestCase):
    """Tests for DiaSemana model"""
    
    def setUp(self):
        self.dia = DiaSemana.objects.create(dia='Segunda-feira')
    
    def test_diasemana_creation(self):
        """Test creating a DiaSemana instance"""
        self.assertEqual(self.dia.dia, 'Segunda-feira')
        self.assertTrue(isinstance(self.dia, DiaSemana))
    
    def test_diasemana_str(self):
        """Test string representation of DiaSemana"""
        self.assertEqual(str(self.dia), 'Segunda-feira')
    
    def test_diasemana_unique_constraint(self):
        """Test that dia field is unique"""
        with self.assertRaises(Exception):
            DiaSemana.objects.create(dia='Segunda-feira')


class TurmaModelTest(TestCase):
    """Tests for Turma model"""
    
    def setUp(self):
        self.segunda = DiaSemana.objects.create(dia='Segunda-feira')
        self.quarta = DiaSemana.objects.create(dia='Quarta-feira')
        self.turma = Turma.objects.create(nome='Turma A', horario='10:00:00')
        self.turma.dias_da_semana.add(self.segunda, self.quarta)
    
    def test_turma_creation(self):
        """Test creating a Turma instance"""
        self.assertEqual(self.turma.nome, 'Turma A')
        self.assertEqual(str(self.turma.horario), '10:00:00')
    
    def test_turma_str(self):
        """Test string representation of Turma"""
        self.assertIn('Turma A', str(self.turma))
    
    def test_turma_many_to_many_dias(self):
        """Test ManyToMany relationship with DiaSemana"""
        self.assertEqual(self.turma.dias_da_semana.count(), 2)
        self.assertIn(self.segunda, self.turma.dias_da_semana.all())
        self.assertIn(self.quarta, self.turma.dias_da_semana.all())
    
    def test_turma_ordering_by_nome(self):
        """Test that Turma is ordered by nome"""
        Turma.objects.create(nome='Turma B', horario='14:00:00')
        Turma.objects.create(nome='Turma C', horario='16:00:00')
        
        turmas = Turma.objects.all()
        self.assertEqual(turmas[0].nome, 'Turma A')
        self.assertEqual(turmas[1].nome, 'Turma B')
        self.assertEqual(turmas[2].nome, 'Turma C')


class AlunoModelTest(TestCase):
    """Tests for Aluno model"""
    
    def setUp(self):
        self.graduacao = Graduacao.objects.create(faixa='Branca')
        self.turma = Turma.objects.create(nome='Turma A', horario='10:00:00')
        self.aluno = Aluno.objects.create(
            nome='João Silva',
            data_nascimento='2010-05-15',
            turma=self.turma,
            graduacao=self.graduacao,
            ativo=True,
            contato='11987654321',
            email='joao@example.com',
            graus=0
        )
    
    def test_aluno_creation(self):
        """Test creating an Aluno instance"""
        self.assertEqual(self.aluno.nome, 'João Silva')
        self.assertTrue(self.aluno.ativo)
        self.assertEqual(self.aluno.graduacao, self.graduacao)
        self.assertEqual(self.aluno.turma, self.turma)
    
    def test_aluno_str(self):
        """Test string representation of Aluno"""
        self.assertEqual(str(self.aluno), 'João Silva')
    
    def test_aluno_defaults(self):
        """Test default values for Aluno"""
        self.assertEqual(self.aluno.graus, 0)
        self.assertTrue(self.aluno.ativo)
        self.assertIsNotNone(self.aluno.data_cadastro)
    
    def test_aluno_optional_fields(self):
        """Test optional fields can be blank"""
        aluno = Aluno.objects.create(
            nome='Maria Santos',
            data_nascimento='2008-03-20'
        )
        self.assertEqual(aluno.contato, '')
        self.assertEqual(aluno.email, '')
        self.assertIsNone(aluno.turma)
        self.assertIsNone(aluno.graduacao)
    
    def test_aluno_ordering_by_nome(self):
        """Test that Aluno is ordered by nome"""
        Aluno.objects.create(nome='Ana', data_nascimento='2010-01-01')
        Aluno.objects.create(nome='Zoe', data_nascimento='2010-01-01')
        
        alunos = Aluno.objects.all()
        self.assertEqual(alunos[0].nome, 'Ana')
        self.assertEqual(alunos[1].nome, 'João Silva')
        self.assertEqual(alunos[2].nome, 'Zoe')
    
    def test_aluno_cascade_turma_deletion(self):
        """Test that Aluno is deleted when Turma is deleted"""
        turma_id = self.turma.id
        aluno_id = self.aluno.id
        
        self.turma.delete()
        
        with self.assertRaises(Aluno.DoesNotExist):
            Aluno.objects.get(id=aluno_id)
    
    def test_aluno_set_null_graduacao_deletion(self):
        """Test that Aluno's graduacao is set to NULL when Graduacao is deleted"""
        graduacao_id = self.graduacao.id
        aluno_id = self.aluno.id
        
        self.graduacao.delete()
        
        aluno = Aluno.objects.get(id=aluno_id)
        self.assertIsNone(aluno.graduacao)
    
    def test_aluno_with_graduation_info(self):
        """Test Aluno with graduation and degree information"""
        aluno = Aluno.objects.create(
            nome='Pedro Costa',
            data_nascimento='2008-01-01',
            graduacao=self.graduacao,
            data_graduacao='2023-06-15',
            graus=2,
            data_grau='2023-06-15',
            responsavel='Pai'
        )
        
        self.assertEqual(aluno.graus, 2)
        self.assertEqual(str(aluno.data_graduacao), '2023-06-15')
        self.assertEqual(aluno.responsavel, 'Pai')


class AlunoInvitationModelTest(TestCase):
    """Tests for AlunoInvitation model"""
    
    def test_invitation_creation(self):
        """Test creating an AlunoInvitation instance"""
        invitation = AlunoInvitation.create_invitation(hours=24)
        
        self.assertIsNotNone(invitation.token)
        self.assertIsNotNone(invitation.expires_at)
        self.assertIsNotNone(invitation.created_at)
    
    def test_invitation_is_valid(self):
        """Test that a new invitation is valid"""
        invitation = AlunoInvitation.create_invitation(hours=24)
        self.assertTrue(invitation.is_valid)
        self.assertFalse(invitation.is_expired)
    
    def test_invitation_is_expired(self):
        """Test that an expired invitation is not valid"""
        invitation = AlunoInvitation.create_invitation(hours=0)
        # Manually set it to past time to ensure expiration
        invitation.expires_at = timezone.now() - timedelta(hours=1)
        invitation.save()
        
        self.assertFalse(invitation.is_valid)
        self.assertTrue(invitation.is_expired)
    
    def test_invitation_token_uniqueness(self):
        """Test that tokens are unique"""
        invitation1 = AlunoInvitation.create_invitation()
        invitation2 = AlunoInvitation.create_invitation()
        
        self.assertNotEqual(invitation1.token, invitation2.token)
    
    def test_invitation_str(self):
        """Test string representation of invitation"""
        invitation = AlunoInvitation.create_invitation()
        self.assertIn('Invitation', str(invitation))
        self.assertIn(invitation.token[:10], str(invitation))
    
    def test_invitation_custom_hours(self):
        """Test invitation with custom expiration hours"""
        invitation = AlunoInvitation.create_invitation(hours=48)
        expected_expires = timezone.now() + timedelta(hours=48)
        
        # Check if expires_at is approximately 48 hours from now (within 1 second)
        time_diff = abs((invitation.expires_at - expected_expires).total_seconds())
        self.assertLess(time_diff, 1)


# ============================================================================
# SERIALIZERS TESTS
# ============================================================================

class GraduacaoSerializerTest(TestCase):
    """Tests for GraduacaoSerializer"""
    
    def setUp(self):
        self.graduacao = Graduacao.objects.create(faixa='Amarela')
    
    def test_serializer_contains_expected_fields(self):
        """Test that serializer contains expected fields"""
        serializer = GraduacaoSerializer(self.graduacao)
        self.assertIn('id', serializer.data)
        self.assertIn('faixa', serializer.data)
    
    def test_serializer_data_matches_model(self):
        """Test that serializer data matches model"""
        serializer = GraduacaoSerializer(self.graduacao)
        self.assertEqual(serializer.data['faixa'], 'Amarela')


class DiaSemanaSerializerTest(TestCase):
    """Tests for DiaSemanaSerializer"""
    
    def setUp(self):
        self.dia = DiaSemana.objects.create(dia='Terça-feira')
    
    def test_serializer_contains_expected_fields(self):
        """Test that serializer contains expected fields"""
        serializer = DiaSemanaSerializer(self.dia)
        self.assertIn('dia', serializer.data)
    
    def test_serializer_data_matches_model(self):
        """Test that serializer data matches model"""
        serializer = DiaSemanaSerializer(self.dia)
        self.assertEqual(serializer.data['dia'], 'Terça-feira')


class TurmaSerializerTest(TestCase):
    """Tests for TurmaSerializer"""
    
    def setUp(self):
        self.segunda = DiaSemana.objects.create(dia='Segunda-feira')
        self.quarta = DiaSemana.objects.create(dia='Quarta-feira')
        self.turma = Turma.objects.create(nome='Turma X', horario='09:00:00')
        self.turma.dias_da_semana.add(self.segunda, self.quarta)
    
    def test_serializer_contains_expected_fields(self):
        """Test that serializer contains expected fields"""
        serializer = TurmaSerializer(self.turma)
        data = serializer.data
        self.assertIn('id', data)
        self.assertIn('nome', data)
        self.assertIn('horario', data)
        self.assertIn('dias', data)
        self.assertIn('dias_da_semana', data)
    
    def test_serializer_dias_method_field(self):
        """Test that dias is correctly generated"""
        serializer = TurmaSerializer(self.turma)
        dias = serializer.data['dias']
        self.assertEqual(len(dias), 2)
        self.assertIn('Segunda-feira', dias)
        self.assertIn('Quarta-feira', dias)


class AlunoSerializerTest(TestCase):
    """Tests for AlunoSerializer"""
    
    def setUp(self):
        self.graduacao = Graduacao.objects.create(faixa='Cinza')
        self.turma = Turma.objects.create(nome='Turma Y', horario='15:00:00')
        self.aluno = Aluno.objects.create(
            nome='Carlos Silva',
            data_nascimento='2009-07-20',
            turma=self.turma,
            graduacao=self.graduacao,
            email='carlos@example.com',
            contato='11999999999'
        )
    
    def test_serializer_contains_expected_fields(self):
        """Test that serializer contains expected fields"""
        serializer = AlunoSerializer(self.aluno)
        data = serializer.data
        self.assertIn('id', data)
        self.assertIn('nome', data)
        self.assertIn('email', data)
        self.assertIn('turma', data)
        self.assertIn('graduacao', data)
        self.assertIn('faixa', data)
        self.assertIn('turma_nome', data)
    
    def test_serializer_data_matches_model(self):
        """Test that serializer data matches model"""
        serializer = AlunoSerializer(self.aluno)
        self.assertEqual(serializer.data['nome'], 'Carlos Silva')
        self.assertEqual(serializer.data['email'], 'carlos@example.com')
        self.assertEqual(serializer.data['faixa'], 'Cinza')
        self.assertEqual(serializer.data['turma_nome'], 'Turma Y')
    
    def test_serializer_foto_base64_none_when_missing(self):
        """Test that foto_base64 is None when photo is missing"""
        serializer = AlunoSerializer(self.aluno)
        self.assertIsNone(serializer.data['foto_base64'])


class AlunoInvitationSerializerTest(TestCase):
    """Tests for AlunoInvitationSerializer"""
    
    def setUp(self):
        self.invitation = AlunoInvitation.create_invitation(hours=24)
    
    def test_serializer_contains_expected_fields(self):
        """Test that serializer contains expected fields"""
        serializer = AlunoInvitationSerializer(self.invitation)
        data = serializer.data
        self.assertIn('token', data)
        self.assertIn('expires_at', data)
        self.assertIn('created_at', data)
        self.assertIn('is_valid', data)
    
    def test_serializer_is_valid_field(self):
        """Test that is_valid field is correctly set"""
        serializer = AlunoInvitationSerializer(self.invitation)
        self.assertTrue(serializer.data['is_valid'])
    
    def test_serializer_is_valid_field_expired(self):
        """Test that is_valid field is False for expired invitation"""
        self.invitation.expires_at = timezone.now() - timedelta(hours=1)
        self.invitation.save()
        
        serializer = AlunoInvitationSerializer(self.invitation)
        self.assertFalse(serializer.data['is_valid'])


# ============================================================================
# API TESTS
# ============================================================================

class AlunoAPITest(APITestCase):
    """Tests for Aluno API endpoints"""
    
    def setUp(self):
        self.client = APIClient()
        self.user = Instrutor.objects.create_user(username='testuser', password='testpass123')
        self.client.force_authenticate(user=self.user)
        
        self.graduacao = Graduacao.objects.create(faixa='Branca')
        self.turma = Turma.objects.create(nome='Turma Test', horario='10:00:00')
        
        # Data for API requests (use IDs)
        self.aluno_data = {
            'nome': 'Test Aluno',
            'data_nascimento': '2010-01-01',
            'turma': self.turma.id,
            'graduacao': self.graduacao.id,
            'email': 'test@example.com',
            'contato': '11999999999',
            'graus': 0
        }
    
    def _create_test_aluno(self, nome='Test Aluno', data_nascimento='2010-01-01'):
        """Helper method to create an Aluno instance with required fields"""
        return Aluno.objects.create(
            nome=nome,
            data_nascimento=data_nascimento,
            turma=self.turma,
            graduacao=self.graduacao,
            email='test@example.com',
            contato='11999999999',
            graus=0
        )
    
    def test_aluno_list_requires_authentication(self):
        """Test that list endpoint requires authentication"""
        self.client.force_authenticate(user=None)
        response = self.client.get('/api/academia/alunos/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_aluno_list_with_authentication(self):
        """Test listing alunos with authentication"""
        self._create_test_aluno()
        response = self.client.get('/api/academia/alunos/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreater(len(response.data['results']), 0)
    
    def test_aluno_create_with_valid_token(self):
        """Test creating aluno with valid invitation token"""
        self.client.force_authenticate(user=None)
        
        invitation = AlunoInvitation.create_invitation(hours=24)
        aluno_data = self.aluno_data.copy()
        aluno_data['invitation_token'] = invitation.token
        
        response = self.client.post('/api/academia/alunos/', aluno_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['nome'], 'Test Aluno')
    
    def test_aluno_create_without_token_returns_error(self):
        """Test creating aluno without token returns error"""
        self.client.force_authenticate(user=None)
        
        response = self.client.post('/api/academia/alunos/', self.aluno_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)
    
    def test_aluno_create_with_invalid_token(self):
        """Test creating aluno with invalid token"""
        self.client.force_authenticate(user=None)
        
        aluno_data = self.aluno_data.copy()
        aluno_data['invitation_token'] = 'invalid_token_xyz'
        
        response = self.client.post('/api/academia/alunos/', aluno_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertIn('error', response.data)
    
    def test_aluno_create_with_expired_token(self):
        """Test creating aluno with expired token"""
        self.client.force_authenticate(user=None)
        
        invitation = AlunoInvitation.create_invitation(hours=0)
        invitation.expires_at = timezone.now() - timedelta(hours=1)
        invitation.save()
        
        aluno_data = self.aluno_data.copy()
        aluno_data['invitation_token'] = invitation.token
        
        response = self.client.post('/api/academia/alunos/', aluno_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_aluno_create_by_authenticated_user_with_token(self):
        """Test that authenticated users can still use token"""
        invitation = AlunoInvitation.create_invitation(hours=24)
        aluno_data = self.aluno_data.copy()
        aluno_data['invitation_token'] = invitation.token
        
        response = self.client.post('/api/academia/alunos/', aluno_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
    
    def test_aluno_retrieve(self):
        """Test retrieving a single aluno"""
        aluno = self._create_test_aluno()
        response = self.client.get(f'/api/academia/alunos/{aluno.id}/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['nome'], 'Test Aluno')
    
    def test_aluno_update(self):
        """Test updating an aluno"""
        aluno = self._create_test_aluno()
        updated_data = self.aluno_data.copy()
        updated_data['nome'] = 'Updated Name'
        
        response = self.client.put(f'/api/academia/alunos/{aluno.id}/', updated_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['nome'], 'Updated Name')
    
    def test_aluno_partial_update(self):
        """Test partial update of an aluno"""
        aluno = self._create_test_aluno()
        
        response = self.client.patch(f'/api/academia/alunos/{aluno.id}/', {'nome': 'Partial Update'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['nome'], 'Partial Update')
    
    def test_aluno_delete(self):
        """Test deleting an aluno"""
        aluno = self._create_test_aluno()
        response = self.client.delete(f'/api/academia/alunos/{aluno.id}/')
        
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        with self.assertRaises(Aluno.DoesNotExist):
            Aluno.objects.get(id=aluno.id)
    
    def test_generate_invitation_requires_authentication(self):
        """Test that generate_invitation requires authentication"""
        self.client.force_authenticate(user=None)
        response = self.client.post('/api/academia/alunos/generate_invitation/', {})
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_generate_invitation_default_hours(self):
        """Test generating invitation with default hours"""
        response = self.client.post('/api/academia/alunos/generate_invitation/', {})
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('token', response.data)
        self.assertIn('expires_at', response.data)
        self.assertTrue(response.data['is_valid'])
    
    def test_generate_invitation_custom_hours(self):
        """Test generating invitation with custom hours"""
        response = self.client.post('/api/academia/alunos/generate_invitation/?hours=48', {})
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(response.data['is_valid'])
    
    def test_generate_invitation_invalid_hours(self):
        """Test that invalid hours parameter is rejected"""
        response = self.client.post('/api/academia/alunos/generate_invitation/?hours=-1', {})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_validate_invitation_valid_token(self):
        """Test validating a valid invitation token"""
        invitation = AlunoInvitation.create_invitation(hours=24)
        
        response = self.client.get(f'/api/academia/alunos/validate_invitation/?token={invitation.token}')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['token'], invitation.token)
        self.assertTrue(response.data['is_valid'])
    
    def test_validate_invitation_invalid_token(self):
        """Test validating an invalid token"""
        response = self.client.get('/api/academia/alunos/validate_invitation/?token=invalid_token')
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIn('error', response.data)
    
    def test_validate_invitation_no_token(self):
        """Test validating without providing a token"""
        response = self.client.get('/api/academia/alunos/validate_invitation/')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)
    
    def test_validate_invitation_expired_token(self):
        """Test validating an expired token"""
        invitation = AlunoInvitation.create_invitation(hours=0)
        invitation.expires_at = timezone.now() - timedelta(hours=1)
        invitation.save()
        
        response = self.client.get(f'/api/academia/alunos/validate_invitation/?token={invitation.token}')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(response.data['is_valid'])
    
    def test_validate_invitation_allows_unauthenticated(self):
        """Test that validate_invitation allows unauthenticated requests"""
        self.client.force_authenticate(user=None)
        invitation = AlunoInvitation.create_invitation(hours=24)
        
        response = self.client.get(f'/api/academia/alunos/validate_invitation/?token={invitation.token}')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class GraduacaoAPITest(APITestCase):
    """Tests for Graduacao API endpoints"""
    
    def setUp(self):
        self.client = APIClient()
        self.user = Instrutor.objects.create_user(username='testuser', password='testpass123')
        self.client.force_authenticate(user=self.user)
        self.graduacao = Graduacao.objects.create(faixa='Azul')
    
    def test_graduacao_list_requires_authentication(self):
        """Test that list endpoint requires authentication"""
        self.client.force_authenticate(user=None)
        response = self.client.get('/api/academia/graduacoes/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_graduacao_list(self):
        """Test listing graduacoes"""
        response = self.client.get('/api/academia/graduacoes/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreater(len(response.data), 0)
    
    def test_graduacao_retrieve(self):
        """Test retrieving a single graduacao"""
        response = self.client.get(f'/api/academia/graduacoes/{self.graduacao.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['faixa'], 'Azul')
    
    def test_graduacao_create(self):
        """Test creating a graduacao"""
        response = self.client.post('/api/academia/graduacoes/', {'faixa': 'Roxa'})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['faixa'], 'Roxa')
    
    def test_graduacao_update(self):
        """Test updating a graduacao"""
        response = self.client.put(f'/api/academia/graduacoes/{self.graduacao.id}/', {'faixa': 'Verde'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['faixa'], 'Verde')
    
    def test_graduacao_delete(self):
        """Test deleting a graduacao"""
        response = self.client.delete(f'/api/academia/graduacoes/{self.graduacao.id}/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)


class TurmaAPITest(APITestCase):
    """Tests for Turma API endpoints"""
    
    def setUp(self):
        self.client = APIClient()
        self.user = Instrutor.objects.create_user(username='testuser', password='testpass123')
        self.client.force_authenticate(user=self.user)
        
        self.segunda = DiaSemana.objects.create(dia='Segunda-feira')
        self.turma = Turma.objects.create(nome='Turma Alpha', horario='09:00:00')
        self.turma.dias_da_semana.add(self.segunda)
    
    def test_turma_list_requires_authentication(self):
        """Test that list endpoint requires authentication"""
        self.client.force_authenticate(user=None)
        response = self.client.get('/api/academia/turmas/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_turma_list(self):
        """Test listing turmas"""
        response = self.client.get('/api/academia/turmas/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreater(len(response.data), 0)
    
    def test_turma_retrieve(self):
        """Test retrieving a single turma"""
        response = self.client.get(f'/api/academia/turmas/{self.turma.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['nome'], 'Turma Alpha')
    
    def test_turma_create(self):
        """Test creating a turma"""
        data = {
            'nome': 'Turma Beta',
            'horario': '14:00:00',
            'dias_da_semana': [self.segunda.id]
        }
        response = self.client.post('/api/academia/turmas/', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['nome'], 'Turma Beta')
    
    def test_turma_update(self):
        """Test updating a turma"""
        data = {
            'nome': 'Turma Gamma',
            'horario': '15:00:00',
            'dias_da_semana': [self.segunda.id]
        }
        response = self.client.put(f'/api/academia/turmas/{self.turma.id}/', data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['nome'], 'Turma Gamma')
    
    def test_turma_delete(self):
        """Test deleting a turma"""
        response = self.client.delete(f'/api/academia/turmas/{self.turma.id}/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)


# ============================================================================
# INTEGRATION TESTS
# ============================================================================

class AlunoInvitationIntegrationTest(APITestCase):
    """Integration tests for the invitation system"""
    
    def setUp(self):
        self.client = APIClient()
        self.user = Instrutor.objects.create_user(username='testuser', password='testpass123')
        self.graduacao = Graduacao.objects.create(faixa='Branca')
        self.turma = Turma.objects.create(nome='Turma Test', horario='10:00:00')
    
    def test_full_invitation_flow(self):
        """Test complete invitation flow: generate, validate, use"""
        # 1. Generate invitation as authenticated user
        self.client.force_authenticate(user=self.user)
        generate_response = self.client.post('/api/academia/alunos/generate_invitation/')
        self.assertEqual(generate_response.status_code, status.HTTP_201_CREATED)
        token = generate_response.data['token']
        
        # 2. Validate invitation as unauthenticated user
        self.client.force_authenticate(user=None)
        validate_response = self.client.get(f'/api/academia/alunos/validate_invitation/?token={token}')
        self.assertEqual(validate_response.status_code, status.HTTP_200_OK)
        self.assertTrue(validate_response.data['is_valid'])
        
        # 3. Use token to create aluno
        aluno_data = {
            'nome': 'Integration Test Aluno',
            'data_nascimento': '2010-01-01',
            'turma': self.turma.id,
            'graduacao': self.graduacao.id,
            'email': 'integration@test.com',
            'invitation_token': token
        }
        create_response = self.client.post('/api/academia/alunos/', aluno_data, format='json')
        self.assertEqual(create_response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(create_response.data['nome'], 'Integration Test Aluno')
    
    def test_multiple_alunos_same_token(self):
        """Test that multiple alunos can be created with the same token"""
        self.client.force_authenticate(user=self.user)
        generate_response = self.client.post('/api/academia/alunos/generate_invitation/')
        token = generate_response.data['token']
        
        self.client.force_authenticate(user=None)
        
        for i in range(3):
            aluno_data = {
                'nome': f'Aluno {i}',
                'data_nascimento': '2010-01-01',
                'invitation_token': token
            }
            response = self.client.post('/api/academia/alunos/', aluno_data, format='json')
            self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Verify all 3 alunos were created
        self.client.force_authenticate(user=self.user)
        list_response = self.client.get('/api/academia/alunos/')
        self.assertEqual(len(list_response.data['results']), 3)
