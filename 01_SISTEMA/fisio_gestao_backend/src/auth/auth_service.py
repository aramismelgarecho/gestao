import jwt
import bcrypt
from datetime import datetime, timedelta
from functools import wraps
from flask import request, jsonify, current_app
from src.models.fisio_models import Fisioterapeuta, db

class AuthService:
    @staticmethod
    def hash_password(password):
        """Criptografar senha usando bcrypt"""
        salt = bcrypt.gensalt()
        return bcrypt.hashpw(password.encode('utf-8'), salt)
    
    @staticmethod
    def verify_password(password, hashed_password):
        """Verificar senha"""
        return bcrypt.checkpw(password.encode('utf-8'), hashed_password)
    
    @staticmethod
    def generate_token(fisioterapeuta_id):
        """Gerar token JWT"""
        payload = {
            'fisioterapeuta_id': fisioterapeuta_id,
            'exp': datetime.utcnow() + timedelta(hours=24),
            'iat': datetime.utcnow()
        }
        return jwt.encode(payload, current_app.config['SECRET_KEY'], algorithm='HS256')
    
    @staticmethod
    def verify_token(token):
        """Verificar e decodificar token JWT"""
        try:
            payload = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=['HS256'])
            return payload['fisioterapeuta_id']
        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None

def token_required(f):
    """Decorator para rotas que requerem autenticação"""
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        
        # Verificar header Authorization
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            try:
                token = auth_header.split(" ")[1]  # Bearer <token>
            except IndexError:
                return jsonify({'erro': 'Token inválido'}), 401
        
        if not token:
            return jsonify({'erro': 'Token de acesso necessário'}), 401
        
        try:
            fisioterapeuta_id = AuthService.verify_token(token)
            if fisioterapeuta_id is None:
                return jsonify({'erro': 'Token inválido ou expirado'}), 401
            
            # Verificar se o fisioterapeuta existe e está ativo
            fisioterapeuta = Fisioterapeuta.query.get(fisioterapeuta_id)
            if not fisioterapeuta or not fisioterapeuta.ativo:
                return jsonify({'erro': 'Usuário inválido ou inativo'}), 401
            
            # Adicionar fisioterapeuta ao contexto da requisição
            request.current_fisioterapeuta = fisioterapeuta
            
        except Exception as e:
            return jsonify({'erro': 'Token inválido'}), 401
        
        return f(*args, **kwargs)
    
    return decorated

def admin_required(f):
    """Decorator para rotas que requerem privilégios administrativos"""
    @wraps(f)
    @token_required
    def decorated(*args, **kwargs):
        if not request.current_fisioterapeuta.is_admin:
            return jsonify({'erro': 'Acesso negado. Privilégios administrativos necessários'}), 403
        
        return f(*args, **kwargs)
    
    return decorated

