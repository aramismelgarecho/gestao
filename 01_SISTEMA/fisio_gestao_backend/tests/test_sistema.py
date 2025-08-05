import pytest
import json
from src.main import app
from src.models.fisio_models import db, Fisioterapeuta, Paciente
from src.auth.auth_service import AuthService

@pytest.fixture
def client():
    """Configurar cliente de teste"""
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
            yield client
            db.drop_all()

@pytest.fixture
def fisioterapeuta_teste(client):
    """Criar fisioterapeuta para testes"""
    fisioterapeuta = Fisioterapeuta(
        nome='Dr. Teste',
        email='teste@fisio.com',
        senha_hash=AuthService.hash_password('senha123'),
        crefito='CREFITO-TEST-123',
        is_admin=False
    )
    db.session.add(fisioterapeuta)
    db.session.commit()
    return fisioterapeuta

@pytest.fixture
def token_auth(client, fisioterapeuta_teste):
    """Gerar token de autenticação para testes"""
    token = AuthService.generate_token(fisioterapeuta_teste.id)
    return f'Bearer {token}'

class TestAutenticacao:
    """Testes para sistema de autenticação"""
    
    def test_cadastro_fisioterapeuta_sucesso(self, client):
        """Testar cadastro de fisioterapeuta com sucesso"""
        data = {
            'nome': 'Dr. João Silva',
            'email': 'joao@fisio.com',
            'senha': 'senha123456',
            'crefito': 'CREFITO-RS-12345'
        }
        
        response = client.post('/api/auth/cadastrar', 
                             data=json.dumps(data),
                             content_type='application/json')
        
        assert response.status_code == 201
        data_response = json.loads(response.data)
        assert 'mensagem' in data_response
        assert 'id' in data_response
    
    def test_cadastro_email_duplicado(self, client, fisioterapeuta_teste):
        """Testar erro ao cadastrar e-mail duplicado"""
        data = {
            'nome': 'Dr. Outro',
            'email': fisioterapeuta_teste.email,
            'senha': 'senha123456',
            'crefito': 'CREFITO-RS-99999'
        }
        
        response = client.post('/api/auth/cadastrar',
                             data=json.dumps(data),
                             content_type='application/json')
        
        assert response.status_code == 409
        data_response = json.loads(response.data)
        assert 'E-mail já cadastrado' in data_response['erro']
    
    def test_login_sucesso(self, client, fisioterapeuta_teste):
        """Testar login com sucesso"""
        data = {
            'email': fisioterapeuta_teste.email,
            'senha': 'senha123'
        }
        
        response = client.post('/api/auth/login',
                             data=json.dumps(data),
                             content_type='application/json')
        
        assert response.status_code == 200
        data_response = json.loads(response.data)
        assert 'token' in data_response
        assert 'fisioterapeuta' in data_response
    
    def test_login_senha_incorreta(self, client, fisioterapeuta_teste):
        """Testar login com senha incorreta"""
        data = {
            'email': fisioterapeuta_teste.email,
            'senha': 'senha_errada'
        }
        
        response = client.post('/api/auth/login',
                             data=json.dumps(data),
                             content_type='application/json')
        
        assert response.status_code == 401
        data_response = json.loads(response.data)
        assert 'Credenciais inválidas' in data_response['erro']
    
    def test_acesso_rota_protegida_sem_token(self, client):
        """Testar acesso a rota protegida sem token"""
        response = client.get('/api/auth/perfil')
        
        assert response.status_code == 401
        data_response = json.loads(response.data)
        assert 'Token de acesso necessário' in data_response['erro']
    
    def test_acesso_rota_protegida_com_token(self, client, token_auth):
        """Testar acesso a rota protegida com token válido"""
        headers = {'Authorization': token_auth}
        response = client.get('/api/auth/perfil', headers=headers)
        
        assert response.status_code == 200
        data_response = json.loads(response.data)
        assert 'nome' in data_response
        assert 'email' in data_response

class TestPacientes:
    """Testes para gestão de pacientes"""
    
    def test_criar_paciente_sucesso(self, client, token_auth):
        """Testar criação de paciente com sucesso"""
        data = {
            'nome_completo': 'Maria Silva Santos',
            'data_nascimento': '1985-03-15',
            'genero': 'Feminino',
            'telefone': '(51) 99999-9999',
            'email': 'maria@email.com',
            'fisioterapeuta_id': 1
        }
        
        headers = {'Authorization': token_auth}
        response = client.post('/api/pacientes',
                             data=json.dumps(data),
                             content_type='application/json',
                             headers=headers)
        
        assert response.status_code == 201
        data_response = json.loads(response.data)
        assert data_response['nome_completo'] == data['nome_completo']
        assert data_response['email'] == data['email']
    
    def test_listar_pacientes(self, client, token_auth):
        """Testar listagem de pacientes"""
        headers = {'Authorization': token_auth}
        response = client.get('/api/pacientes', headers=headers)
        
        assert response.status_code == 200
        data_response = json.loads(response.data)
        assert isinstance(data_response, list)
    
    def test_criar_paciente_sem_nome(self, client, token_auth):
        """Testar erro ao criar paciente sem nome"""
        data = {
            'data_nascimento': '1985-03-15',
            'fisioterapeuta_id': 1
        }
        
        headers = {'Authorization': token_auth}
        response = client.post('/api/pacientes',
                             data=json.dumps(data),
                             content_type='application/json',
                             headers=headers)
        
        assert response.status_code == 400

class TestLGPD:
    """Testes para conformidade com LGPD"""
    
    def test_registrar_consentimento(self, client, token_auth):
        """Testar registro de consentimento LGPD"""
        # Primeiro criar um paciente
        paciente_data = {
            'nome_completo': 'Paciente Teste LGPD',
            'data_nascimento': '1990-01-01',
            'fisioterapeuta_id': 1
        }
        
        headers = {'Authorization': token_auth}
        response = client.post('/api/pacientes',
                             data=json.dumps(paciente_data),
                             content_type='application/json',
                             headers=headers)
        
        paciente_id = json.loads(response.data)['id']
        
        # Registrar consentimento
        consentimento_data = {
            'consentimento_tratamento_dados': True,
            'consentimento_comunicacao': False,
            'consentimento_pesquisa': True,
            'versao_termos': '1.0'
        }
        
        response = client.post(f'/api/lgpd/consentimento/{paciente_id}',
                             data=json.dumps(consentimento_data),
                             content_type='application/json',
                             headers=headers)
        
        assert response.status_code == 200
        data_response = json.loads(response.data)
        assert 'mensagem' in data_response
        assert 'data_consentimento' in data_response
    
    def test_exportar_dados_paciente_json(self, client, token_auth):
        """Testar exportação de dados do paciente em JSON"""
        # Criar paciente
        paciente_data = {
            'nome_completo': 'Paciente Exportação',
            'data_nascimento': '1985-05-15',
            'email': 'exportacao@teste.com',
            'fisioterapeuta_id': 1
        }
        
        headers = {'Authorization': token_auth}
        response = client.post('/api/pacientes',
                             data=json.dumps(paciente_data),
                             content_type='application/json',
                             headers=headers)
        
        paciente_id = json.loads(response.data)['id']
        
        # Exportar dados
        response = client.get(f'/api/lgpd/portabilidade/{paciente_id}?formato=json',
                            headers=headers)
        
        assert response.status_code == 200
        data_response = json.loads(response.data)
        assert 'dados' in data_response
        assert 'informacoes_pessoais' in data_response['dados']
        assert data_response['dados']['informacoes_pessoais']['nome_completo'] == paciente_data['nome_completo']

class TestSeguranca:
    """Testes para funcionalidades de segurança"""
    
    def test_bloqueio_conta_tentativas_login(self, client):
        """Testar bloqueio de conta após múltiplas tentativas de login"""
        # Criar fisioterapeuta
        fisioterapeuta = Fisioterapeuta(
            nome='Dr. Bloqueio',
            email='bloqueio@teste.com',
            senha_hash=AuthService.hash_password('senha123'),
            crefito='CREFITO-BLOQ-123'
        )
        db.session.add(fisioterapeuta)
        db.session.commit()
        
        # Fazer 5 tentativas de login com senha incorreta
        for i in range(5):
            data = {
                'email': 'bloqueio@teste.com',
                'senha': 'senha_errada'
            }
            
            response = client.post('/api/auth/login',
                                 data=json.dumps(data),
                                 content_type='application/json')
            
            assert response.status_code == 401
        
        # Verificar se a conta foi bloqueada
        fisioterapeuta_atualizado = Fisioterapeuta.query.filter_by(email='bloqueio@teste.com').first()
        assert fisioterapeuta_atualizado.conta_bloqueada == True
        assert fisioterapeuta_atualizado.tentativas_login_falhadas >= 5
    
    def test_alteracao_senha(self, client, token_auth, fisioterapeuta_teste):
        """Testar alteração de senha"""
        data = {
            'senha_atual': 'senha123',
            'senha_nova': 'nova_senha_123'
        }
        
        headers = {'Authorization': token_auth}
        response = client.put('/api/auth/alterar-senha',
                            data=json.dumps(data),
                            content_type='application/json',
                            headers=headers)
        
        assert response.status_code == 200
        data_response = json.loads(response.data)
        assert 'Senha alterada com sucesso' in data_response['mensagem']

class TestValidacaoRequisitos:
    """Testes para validar atendimento aos requisitos"""
    
    def test_campos_obrigatorios_coffito(self, client, token_auth):
        """Testar se campos obrigatórios do COFFITO estão implementados"""
        data = {
            'nome_completo': 'Paciente COFFITO',
            'data_nascimento': '1980-12-25',
            'genero': 'Masculino',
            'estado_civil': 'Solteiro',
            'profissao': 'Engenheiro',
            'naturalidade': 'Porto Alegre',
            'local_nascimento': 'Porto Alegre, RS',
            'telefone': '(51) 88888-8888',
            'endereco_residencial': 'Rua Teste, 123',
            'fisioterapeuta_id': 1
        }
        
        headers = {'Authorization': token_auth}
        response = client.post('/api/pacientes',
                             data=json.dumps(data),
                             content_type='application/json',
                             headers=headers)
        
        assert response.status_code == 201
        data_response = json.loads(response.data)
        
        # Verificar se todos os campos COFFITO estão presentes
        campos_coffito = [
            'nome_completo', 'data_nascimento', 'genero', 'estado_civil',
            'profissao', 'naturalidade', 'local_nascimento'
        ]
        
        for campo in campos_coffito:
            assert campo in data_response
            assert data_response[campo] == data[campo]
    
    def test_campos_lgpd_implementados(self, client, token_auth):
        """Testar se campos LGPD estão implementados"""
        # Criar paciente
        data = {
            'nome_completo': 'Paciente LGPD',
            'data_nascimento': '1990-06-15',
            'fisioterapeuta_id': 1
        }
        
        headers = {'Authorization': token_auth}
        response = client.post('/api/pacientes',
                             data=json.dumps(data),
                             content_type='application/json',
                             headers=headers)
        
        assert response.status_code == 201
        data_response = json.loads(response.data)
        
        # Verificar se campos LGPD estão presentes
        campos_lgpd = [
            'consentimento_tratamento_dados',
            'consentimento_comunicacao',
            'consentimento_pesquisa',
            'versao_termos'
        ]
        
        for campo in campos_lgpd:
            assert campo in data_response

