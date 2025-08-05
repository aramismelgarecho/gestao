from flask import Blueprint, jsonify, request
from src.models.fisio_models import Procedimento, db
from datetime import datetime

procedimento_bp = Blueprint('procedimento', __name__)

@procedimento_bp.route('/procedimentos', methods=['GET'])
def get_procedimentos():
    """Listar procedimentos com filtros opcionais"""
    try:
        ativo = request.args.get('ativo', type=bool)
        nome = request.args.get('nome', '')
        
        query = Procedimento.query
        
        if ativo is not None:
            query = query.filter(Procedimento.ativo == ativo)
        
        if nome:
            query = query.filter(Procedimento.nome.ilike(f'%{nome}%'))
        
        procedimentos = query.order_by(Procedimento.nome).all()
        return jsonify([procedimento.to_dict() for procedimento in procedimentos])
    
    except Exception as e:
        return jsonify({'erro': str(e)}), 500

@procedimento_bp.route('/procedimentos', methods=['POST'])
def create_procedimento():
    """Criar novo procedimento"""
    try:
        data = request.json
        
        # Validações obrigatórias
        if not data.get('nome'):
            return jsonify({'erro': 'Nome do procedimento é obrigatório'}), 400
        
        procedimento = Procedimento(
            nome=data['nome'],
            descricao=data.get('descricao'),
            duracao_minutos=data.get('duracao_minutos'),
            codigo=data.get('codigo')
        )
        
        db.session.add(procedimento)
        db.session.commit()
        
        return jsonify(procedimento.to_dict()), 201
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'erro': str(e)}), 500

@procedimento_bp.route('/procedimentos/<int:procedimento_id>', methods=['GET'])
def get_procedimento(procedimento_id):
    """Obter procedimento por ID"""
    try:
        procedimento = Procedimento.query.get_or_404(procedimento_id)
        return jsonify(procedimento.to_dict())
    
    except Exception as e:
        return jsonify({'erro': str(e)}), 500

@procedimento_bp.route('/procedimentos/<int:procedimento_id>', methods=['PUT'])
def update_procedimento(procedimento_id):
    """Atualizar procedimento"""
    try:
        procedimento = Procedimento.query.get_or_404(procedimento_id)
        data = request.json
        
        # Atualizar campos
        if 'nome' in data:
            procedimento.nome = data['nome']
        if 'descricao' in data:
            procedimento.descricao = data['descricao']
        if 'duracao_minutos' in data:
            procedimento.duracao_minutos = data['duracao_minutos']
        if 'codigo' in data:
            procedimento.codigo = data['codigo']
        if 'ativo' in data:
            procedimento.ativo = data['ativo']
        
        procedimento.data_atualizacao = datetime.utcnow()
        db.session.commit()
        
        return jsonify(procedimento.to_dict())
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'erro': str(e)}), 500

@procedimento_bp.route('/procedimentos/<int:procedimento_id>', methods=['DELETE'])
def delete_procedimento(procedimento_id):
    """Desativar procedimento (soft delete)"""
    try:
        procedimento = Procedimento.query.get_or_404(procedimento_id)
        
        # Soft delete - marcar como inativo
        procedimento.ativo = False
        procedimento.data_atualizacao = datetime.utcnow()
        
        db.session.commit()
        
        return jsonify({'mensagem': 'Procedimento desativado com sucesso'}), 200
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'erro': str(e)}), 500

