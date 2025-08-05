from flask import Blueprint, jsonify, request
from src.models.fisio_models import Paciente, db
from datetime import datetime

paciente_bp = Blueprint('paciente', __name__)

@paciente_bp.route('/pacientes', methods=['GET'])
def get_pacientes():
    """Listar pacientes com filtros opcionais"""
    try:
        # Parâmetros de filtro
        ativo = request.args.get('ativo', type=bool)
        arquivado = request.args.get('arquivado', type=bool)
        fisioterapeuta_id = request.args.get('fisioterapeuta_id', type=int)
        nome = request.args.get('nome', '')
        
        # Construir query
        query = Paciente.query
        
        if ativo is not None:
            query = query.filter(Paciente.ativo == ativo)
        
        if arquivado is not None:
            query = query.filter(Paciente.arquivado == arquivado)
        
        if fisioterapeuta_id:
            query = query.filter(Paciente.fisioterapeuta_id == fisioterapeuta_id)
        
        if nome:
            query = query.filter(Paciente.nome_completo.ilike(f'%{nome}%'))
        
        pacientes = query.all()
        return jsonify([paciente.to_dict() for paciente in pacientes])
    
    except Exception as e:
        return jsonify({'erro': str(e)}), 500

@paciente_bp.route('/pacientes', methods=['POST'])
def create_paciente():
    """Criar novo paciente"""
    try:
        data = request.json
        
        # Validações obrigatórias
        if not data.get('nome_completo'):
            return jsonify({'erro': 'Nome completo é obrigatório'}), 400
        
        if not data.get('data_nascimento'):
            return jsonify({'erro': 'Data de nascimento é obrigatória'}), 400
        
        if not data.get('fisioterapeuta_id'):
            return jsonify({'erro': 'Fisioterapeuta é obrigatório'}), 400
        
        # Converter data de nascimento
        try:
            data_nascimento = datetime.strptime(data['data_nascimento'], '%Y-%m-%d').date()
        except ValueError:
            return jsonify({'erro': 'Formato de data inválido. Use YYYY-MM-DD'}), 400
        
        paciente = Paciente(
            nome_completo=data['nome_completo'],
            naturalidade=data.get('naturalidade'),
            estado_civil=data.get('estado_civil'),
            genero=data.get('genero'),
            local_nascimento=data.get('local_nascimento'),
            data_nascimento=data_nascimento,
            profissao=data.get('profissao'),
            endereco_residencial=data.get('endereco_residencial'),
            endereco_comercial=data.get('endereco_comercial'),
            telefone=data.get('telefone'),
            email=data.get('email'),
            fisioterapeuta_id=data['fisioterapeuta_id']
        )
        
        db.session.add(paciente)
        db.session.commit()
        
        return jsonify(paciente.to_dict()), 201
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'erro': str(e)}), 500

@paciente_bp.route('/pacientes/<int:paciente_id>', methods=['GET'])
def get_paciente(paciente_id):
    """Obter paciente por ID"""
    try:
        paciente = Paciente.query.get_or_404(paciente_id)
        return jsonify(paciente.to_dict())
    
    except Exception as e:
        return jsonify({'erro': str(e)}), 500

@paciente_bp.route('/pacientes/<int:paciente_id>', methods=['PUT'])
def update_paciente(paciente_id):
    """Atualizar paciente"""
    try:
        paciente = Paciente.query.get_or_404(paciente_id)
        data = request.json
        
        # Atualizar campos
        if 'nome_completo' in data:
            paciente.nome_completo = data['nome_completo']
        if 'naturalidade' in data:
            paciente.naturalidade = data['naturalidade']
        if 'estado_civil' in data:
            paciente.estado_civil = data['estado_civil']
        if 'genero' in data:
            paciente.genero = data['genero']
        if 'local_nascimento' in data:
            paciente.local_nascimento = data['local_nascimento']
        if 'data_nascimento' in data:
            try:
                paciente.data_nascimento = datetime.strptime(data['data_nascimento'], '%Y-%m-%d').date()
            except ValueError:
                return jsonify({'erro': 'Formato de data inválido. Use YYYY-MM-DD'}), 400
        if 'profissao' in data:
            paciente.profissao = data['profissao']
        if 'endereco_residencial' in data:
            paciente.endereco_residencial = data['endereco_residencial']
        if 'endereco_comercial' in data:
            paciente.endereco_comercial = data['endereco_comercial']
        if 'telefone' in data:
            paciente.telefone = data['telefone']
        if 'email' in data:
            paciente.email = data['email']
        
        paciente.data_atualizacao = datetime.utcnow()
        db.session.commit()
        
        return jsonify(paciente.to_dict())
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'erro': str(e)}), 500

@paciente_bp.route('/pacientes/<int:paciente_id>', methods=['DELETE'])
def delete_paciente(paciente_id):
    """Soft delete de paciente (LGPD compliance)"""
    try:
        paciente = Paciente.query.get_or_404(paciente_id)
        
        # Soft delete - marcar como inativo
        paciente.ativo = False
        paciente.data_atualizacao = datetime.utcnow()
        
        db.session.commit()
        
        # Log da operação de exclusão (para auditoria LGPD)
        # TODO: Implementar sistema de logs de auditoria
        
        return jsonify({'mensagem': 'Paciente excluído com sucesso'}), 200
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'erro': str(e)}), 500

@paciente_bp.route('/pacientes/<int:paciente_id>/arquivar', methods=['PUT'])
def arquivar_paciente(paciente_id):
    """Arquivar/desarquivar paciente"""
    try:
        paciente = Paciente.query.get_or_404(paciente_id)
        data = request.json
        
        arquivar = data.get('arquivar', True)
        paciente.arquivado = arquivar
        paciente.data_atualizacao = datetime.utcnow()
        
        db.session.commit()
        
        status = 'arquivado' if arquivar else 'desarquivado'
        return jsonify({'mensagem': f'Paciente {status} com sucesso'})
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'erro': str(e)}), 500

@paciente_bp.route('/pacientes/<int:paciente_id>/prontuario', methods=['GET'])
def get_prontuario_paciente(paciente_id):
    """Obter prontuário completo do paciente"""
    try:
        paciente = Paciente.query.get_or_404(paciente_id)
        
        # Buscar todas as informações relacionadas
        avaliacoes = [avaliacao.to_dict() for avaliacao in paciente.avaliacoes]
        evolucoes = [evolucao.to_dict() for evolucao in paciente.evolucoes]
        agendamentos = [agendamento.to_dict() for agendamento in paciente.agendamentos]
        
        prontuario = {
            'paciente': paciente.to_dict(),
            'avaliacoes': avaliacoes,
            'evolucoes': evolucoes,
            'agendamentos': agendamentos
        }
        
        return jsonify(prontuario)
    
    except Exception as e:
        return jsonify({'erro': str(e)}), 500

