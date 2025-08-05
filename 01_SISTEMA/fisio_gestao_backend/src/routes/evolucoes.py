from flask import Blueprint, jsonify, request
from src.models.fisio_models import Evolucao, Paciente, Avaliacao, ProcedimentoEvolucao, Procedimento, db
from datetime import datetime

evolucao_bp = Blueprint('evolucao', __name__)

@evolucao_bp.route('/evolucoes', methods=['GET'])
def get_evolucoes():
    """Listar evoluções com filtros opcionais"""
    try:
        paciente_id = request.args.get('paciente_id', type=int)
        avaliacao_id = request.args.get('avaliacao_id', type=int)
        
        query = Evolucao.query
        
        if paciente_id:
            query = query.filter(Evolucao.paciente_id == paciente_id)
        
        if avaliacao_id:
            query = query.filter(Evolucao.avaliacao_id == avaliacao_id)
        
        evolucoes = query.order_by(Evolucao.data_sessao.desc()).all()
        
        # Incluir procedimentos nas evoluções
        evolucoes_dict = []
        for evolucao in evolucoes:
            evolucao_dict = evolucao.to_dict()
            evolucao_dict['procedimentos'] = [proc.to_dict() for proc in evolucao.procedimentos]
            evolucoes_dict.append(evolucao_dict)
        
        return jsonify(evolucoes_dict)
    
    except Exception as e:
        return jsonify({'erro': str(e)}), 500

@evolucao_bp.route('/evolucoes', methods=['POST'])
def create_evolucao():
    """Criar nova evolução"""
    try:
        data = request.json
        
        # Validações obrigatórias
        if not data.get('paciente_id'):
            return jsonify({'erro': 'Paciente é obrigatório'}), 400
        
        if not data.get('data_sessao'):
            return jsonify({'erro': 'Data da sessão é obrigatória'}), 400
        
        # Verificar se o paciente existe
        paciente = Paciente.query.get(data['paciente_id'])
        if not paciente:
            return jsonify({'erro': 'Paciente não encontrado'}), 404
        
        # Verificar se a avaliação existe (se fornecida)
        if data.get('avaliacao_id'):
            avaliacao = Avaliacao.query.get(data['avaliacao_id'])
            if not avaliacao:
                return jsonify({'erro': 'Avaliação não encontrada'}), 404
        
        # Converter data da sessão
        try:
            data_sessao = datetime.fromisoformat(data['data_sessao'].replace('Z', '+00:00'))
        except ValueError:
            return jsonify({'erro': 'Formato de data inválido'}), 400
        
        evolucao = Evolucao(
            paciente_id=data['paciente_id'],
            avaliacao_id=data.get('avaliacao_id'),
            data_sessao=data_sessao,
            procedimentos_realizados=data.get('procedimentos_realizados'),
            resposta_paciente=data.get('resposta_paciente'),
            intercorrencias=data.get('intercorrencias'),
            observacoes=data.get('observacoes')
        )
        
        db.session.add(evolucao)
        db.session.flush()  # Para obter o ID da evolução
        
        # Adicionar procedimentos se fornecidos
        procedimentos_ids = data.get('procedimentos_ids', [])
        for proc_data in procedimentos_ids:
            if isinstance(proc_data, dict):
                procedimento_id = proc_data.get('procedimento_id')
                observacoes_proc = proc_data.get('observacoes', '')
            else:
                procedimento_id = proc_data
                observacoes_proc = ''
            
            if procedimento_id:
                # Verificar se o procedimento existe
                procedimento = Procedimento.query.get(procedimento_id)
                if procedimento:
                    proc_evolucao = ProcedimentoEvolucao(
                        evolucao_id=evolucao.id,
                        procedimento_id=procedimento_id,
                        observacoes=observacoes_proc
                    )
                    db.session.add(proc_evolucao)
        
        db.session.commit()
        
        # Retornar evolução com procedimentos
        evolucao_dict = evolucao.to_dict()
        evolucao_dict['procedimentos'] = [proc.to_dict() for proc in evolucao.procedimentos]
        
        return jsonify(evolucao_dict), 201
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'erro': str(e)}), 500

@evolucao_bp.route('/evolucoes/<int:evolucao_id>', methods=['GET'])
def get_evolucao(evolucao_id):
    """Obter evolução por ID"""
    try:
        evolucao = Evolucao.query.get_or_404(evolucao_id)
        
        # Incluir procedimentos na resposta
        evolucao_dict = evolucao.to_dict()
        evolucao_dict['procedimentos'] = [proc.to_dict() for proc in evolucao.procedimentos]
        
        return jsonify(evolucao_dict)
    
    except Exception as e:
        return jsonify({'erro': str(e)}), 500

@evolucao_bp.route('/evolucoes/<int:evolucao_id>', methods=['PUT'])
def update_evolucao(evolucao_id):
    """Atualizar evolução"""
    try:
        evolucao = Evolucao.query.get_or_404(evolucao_id)
        data = request.json
        
        # Atualizar campos básicos
        if 'data_sessao' in data:
            try:
                evolucao.data_sessao = datetime.fromisoformat(data['data_sessao'].replace('Z', '+00:00'))
            except ValueError:
                return jsonify({'erro': 'Formato de data inválido'}), 400
        
        if 'procedimentos_realizados' in data:
            evolucao.procedimentos_realizados = data['procedimentos_realizados']
        
        if 'resposta_paciente' in data:
            evolucao.resposta_paciente = data['resposta_paciente']
        
        if 'intercorrencias' in data:
            evolucao.intercorrencias = data['intercorrencias']
        
        if 'observacoes' in data:
            evolucao.observacoes = data['observacoes']
        
        if 'avaliacao_id' in data:
            evolucao.avaliacao_id = data['avaliacao_id']
        
        # Atualizar procedimentos se fornecidos
        if 'procedimentos_ids' in data:
            # Remover procedimentos existentes
            ProcedimentoEvolucao.query.filter_by(evolucao_id=evolucao_id).delete()
            
            # Adicionar novos procedimentos
            procedimentos_ids = data['procedimentos_ids']
            for proc_data in procedimentos_ids:
                if isinstance(proc_data, dict):
                    procedimento_id = proc_data.get('procedimento_id')
                    observacoes_proc = proc_data.get('observacoes', '')
                else:
                    procedimento_id = proc_data
                    observacoes_proc = ''
                
                if procedimento_id:
                    procedimento = Procedimento.query.get(procedimento_id)
                    if procedimento:
                        proc_evolucao = ProcedimentoEvolucao(
                            evolucao_id=evolucao_id,
                            procedimento_id=procedimento_id,
                            observacoes=observacoes_proc
                        )
                        db.session.add(proc_evolucao)
        
        evolucao.data_atualizacao = datetime.utcnow()
        db.session.commit()
        
        # Retornar evolução atualizada com procedimentos
        evolucao_dict = evolucao.to_dict()
        evolucao_dict['procedimentos'] = [proc.to_dict() for proc in evolucao.procedimentos]
        
        return jsonify(evolucao_dict)
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'erro': str(e)}), 500

@evolucao_bp.route('/evolucoes/<int:evolucao_id>', methods=['DELETE'])
def delete_evolucao(evolucao_id):
    """Excluir evolução"""
    try:
        evolucao = Evolucao.query.get_or_404(evolucao_id)
        
        # Excluir procedimentos relacionados (cascade já configurado no modelo)
        db.session.delete(evolucao)
        db.session.commit()
        
        return jsonify({'mensagem': 'Evolução excluída com sucesso'}), 200
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'erro': str(e)}), 500

