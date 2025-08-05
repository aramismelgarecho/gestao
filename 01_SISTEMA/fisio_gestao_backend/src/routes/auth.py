from flask import Blueprint, jsonify, request
from src.models.fisio_models import Fisioterapeuta, db
from src.auth.auth_service import AuthService, token_required
from src.audit.audit_service import AuditoriaService
from datetime import datetime
import json

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/auth/login', methods=['POST'])
def login():
    """Autenticar fisioterapeuta"""
    try:
        data = request.json
        
        if not data.get('email') or not data.get('senha'):
            return jsonify({'erro': 'E-mail e senha são obrigatórios'}), 400
        
        # Buscar fisioterapeuta por e-mail
        fisioterapeuta = Fisioterapeuta.query.filter_by(email=data['email']).first()
        
        if not fisioterapeuta:
            # Log de tentativa de login inválida
            AuditoriaService.log_acao(
                acao='LOGIN_FALHOU',
                sucesso=False,
                observacoes=f'E-mail não encontrado: {data["email"]}'
            )
            return jsonify({'erro': 'Credenciais inválidas'}), 401
        
        if not fisioterapeuta.ativo:
            # Log de tentativa de login com conta inativa
            AuditoriaService.log_acao(
                acao='LOGIN_FALHOU',
                fisioterapeuta_id=fisioterapeuta.id,
                sucesso=False,
                observacoes='Conta inativa'
            )
            return jsonify({'erro': 'Conta inativa'}), 401
        
        # Verificar senha
        if not AuthService.verify_password(data['senha'], fisioterapeuta.senha_hash):
            # Incrementar tentativas de login falhadas
            fisioterapeuta.tentativas_login_falhadas += 1
            fisioterapeuta.data_ultima_tentativa_login = datetime.utcnow()
            
            # Bloquear conta após 5 tentativas
            if fisioterapeuta.tentativas_login_falhadas >= 5:
                fisioterapeuta.conta_bloqueada = True
                fisioterapeuta.data_bloqueio = datetime.utcnow()
            
            db.session.commit()
            
            # Log de tentativa de login inválida
            AuditoriaService.log_acao(
                acao='LOGIN_FALHOU',
                fisioterapeuta_id=fisioterapeuta.id,
                sucesso=False,
                observacoes=f'Senha incorreta. Tentativas: {fisioterapeuta.tentativas_login_falhadas}'
            )
            
            return jsonify({'erro': 'Credenciais inválidas'}), 401
        
        # Verificar se a conta está bloqueada
        if fisioterapeuta.conta_bloqueada:
            AuditoriaService.log_acao(
                acao='LOGIN_FALHOU',
                fisioterapeuta_id=fisioterapeuta.id,
                sucesso=False,
                observacoes='Conta bloqueada'
            )
            return jsonify({'erro': 'Conta bloqueada. Entre em contato com o administrador'}), 401
        
        # Login bem-sucedido
        token = AuthService.generate_token(fisioterapeuta.id)
        
        # Resetar tentativas de login e atualizar último acesso
        fisioterapeuta.tentativas_login_falhadas = 0
        fisioterapeuta.data_ultimo_login = datetime.utcnow()
        fisioterapeuta.data_ultima_tentativa_login = datetime.utcnow()
        
        db.session.commit()
        
        # Log de login bem-sucedido
        AuditoriaService.log_acao(
            acao='LOGIN_SUCESSO',
            fisioterapeuta_id=fisioterapeuta.id,
            sucesso=True
        )
        
        return jsonify({
            'token': token,
            'fisioterapeuta': {
                'id': fisioterapeuta.id,
                'nome': fisioterapeuta.nome,
                'email': fisioterapeuta.email,
                'crefito': fisioterapeuta.crefito,
                'is_admin': fisioterapeuta.is_admin
            }
        })
    
    except Exception as e:
        return jsonify({'erro': str(e)}), 500

@auth_bp.route('/auth/logout', methods=['POST'])
@token_required
def logout():
    """Logout do fisioterapeuta"""
    try:
        # Log de logout
        AuditoriaService.log_acao(
            acao='LOGOUT',
            fisioterapeuta_id=request.current_fisioterapeuta.id,
            sucesso=True
        )
        
        return jsonify({'mensagem': 'Logout realizado com sucesso'})
    
    except Exception as e:
        return jsonify({'erro': str(e)}), 500

@auth_bp.route('/auth/perfil', methods=['GET'])
@token_required
def get_perfil():
    """Obter perfil do fisioterapeuta autenticado"""
    try:
        fisioterapeuta = request.current_fisioterapeuta
        
        return jsonify({
            'id': fisioterapeuta.id,
            'nome': fisioterapeuta.nome,
            'email': fisioterapeuta.email,
            'crefito': fisioterapeuta.crefito,
            'especialidade': fisioterapeuta.especialidade,
            'telefone': fisioterapeuta.telefone,
            'is_admin': fisioterapeuta.is_admin,
            'data_ultimo_login': fisioterapeuta.data_ultimo_login.isoformat() if fisioterapeuta.data_ultimo_login else None,
            'data_criacao': fisioterapeuta.data_criacao.isoformat() if fisioterapeuta.data_criacao else None
        })
    
    except Exception as e:
        return jsonify({'erro': str(e)}), 500

@auth_bp.route('/auth/alterar-senha', methods=['PUT'])
@token_required
def alterar_senha():
    """Alterar senha do fisioterapeuta"""
    try:
        data = request.json
        fisioterapeuta = request.current_fisioterapeuta
        
        if not data.get('senha_atual') or not data.get('senha_nova'):
            return jsonify({'erro': 'Senha atual e nova senha são obrigatórias'}), 400
        
        # Verificar senha atual
        if not AuthService.verify_password(data['senha_atual'], fisioterapeuta.senha_hash):
            # Log de tentativa de alteração com senha incorreta
            AuditoriaService.log_acao(
                acao='ALTERACAO_SENHA_FALHOU',
                fisioterapeuta_id=fisioterapeuta.id,
                sucesso=False,
                observacoes='Senha atual incorreta'
            )
            return jsonify({'erro': 'Senha atual incorreta'}), 401
        
        # Validar nova senha (mínimo 8 caracteres)
        if len(data['senha_nova']) < 8:
            return jsonify({'erro': 'Nova senha deve ter pelo menos 8 caracteres'}), 400
        
        # Atualizar senha
        fisioterapeuta.senha_hash = AuthService.hash_password(data['senha_nova'])
        fisioterapeuta.data_alteracao_senha = datetime.utcnow()
        
        db.session.commit()
        
        # Log de alteração de senha bem-sucedida
        AuditoriaService.log_acao(
            acao='ALTERACAO_SENHA_SUCESSO',
            fisioterapeuta_id=fisioterapeuta.id,
            sucesso=True
        )
        
        return jsonify({'mensagem': 'Senha alterada com sucesso'})
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'erro': str(e)}), 500

@auth_bp.route('/auth/desbloquear-conta/<int:fisioterapeuta_id>', methods=['PUT'])
@token_required
def desbloquear_conta(fisioterapeuta_id):
    """Desbloquear conta de fisioterapeuta (apenas admin)"""
    try:
        if not request.current_fisioterapeuta.is_admin:
            return jsonify({'erro': 'Acesso negado. Apenas administradores podem desbloquear contas'}), 403
        
        fisioterapeuta = Fisioterapeuta.query.get_or_404(fisioterapeuta_id)
        
        fisioterapeuta.conta_bloqueada = False
        fisioterapeuta.tentativas_login_falhadas = 0
        fisioterapeuta.data_bloqueio = None
        
        db.session.commit()
        
        # Log de desbloqueio
        AuditoriaService.log_acao(
            acao='CONTA_DESBLOQUEADA',
            fisioterapeuta_id=fisioterapeuta_id,
            sucesso=True,
            observacoes=f'Desbloqueada por admin: {request.current_fisioterapeuta.id}'
        )
        
        return jsonify({'mensagem': 'Conta desbloqueada com sucesso'})
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'erro': str(e)}), 500

@auth_bp.route('/auth/cadastrar', methods=['POST'])
def cadastrar_fisioterapeuta():
    """Cadastrar novo fisioterapeuta"""
    try:
        data = request.json
        
        # Validações obrigatórias
        campos_obrigatorios = ['nome', 'email', 'senha', 'crefito']
        for campo in campos_obrigatorios:
            if not data.get(campo):
                return jsonify({'erro': f'{campo} é obrigatório'}), 400
        
        # Verificar se e-mail já existe
        if Fisioterapeuta.query.filter_by(email=data['email']).first():
            return jsonify({'erro': 'E-mail já cadastrado'}), 409
        
        # Verificar se CREFITO já existe
        if Fisioterapeuta.query.filter_by(crefito=data['crefito']).first():
            return jsonify({'erro': 'CREFITO já cadastrado'}), 409
        
        # Validar senha
        if len(data['senha']) < 8:
            return jsonify({'erro': 'Senha deve ter pelo menos 8 caracteres'}), 400
        
        # Criar fisioterapeuta
        fisioterapeuta = Fisioterapeuta(
            nome=data['nome'],
            email=data['email'],
            senha_hash=AuthService.hash_password(data['senha']),
            crefito=data['crefito'],
            especialidade=data.get('especialidade'),
            telefone=data.get('telefone'),
            is_admin=data.get('is_admin', False)
        )
        
        db.session.add(fisioterapeuta)
        db.session.commit()
        
        # Log de cadastro
        AuditoriaService.log_acao(
            acao='FISIOTERAPEUTA_CADASTRADO',
            tabela='fisioterapeutas',
            registro_id=fisioterapeuta.id,
            dados_novos=json.dumps({
                'nome': fisioterapeuta.nome,
                'email': fisioterapeuta.email,
                'crefito': fisioterapeuta.crefito
            }),
            sucesso=True
        )
        
        return jsonify({
            'mensagem': 'Fisioterapeuta cadastrado com sucesso',
            'id': fisioterapeuta.id
        }), 201
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'erro': str(e)}), 500

