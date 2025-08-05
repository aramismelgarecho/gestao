from flask import Blueprint, jsonify, request
from src.models.fisio_models import Agendamento, Paciente, db
from datetime import datetime, timedelta

agendamento_bp = Blueprint('agendamento', __name__)

@agendamento_bp.route('/agendamentos', methods=['GET'])
def get_agendamentos():
    """Listar agendamentos com filtros opcionais"""
    try:
        paciente_id = request.args.get('paciente_id', type=int)
        status = request.args.get('status')
        data_inicio = request.args.get('data_inicio')
        data_fim = request.args.get('data_fim')
        
        query = Agendamento.query
        
        if paciente_id:
            query = query.filter(Agendamento.paciente_id == paciente_id)
        
        if status:
            query = query.filter(Agendamento.status == status)
        
        if data_inicio:
            try:
                data_inicio_dt = datetime.fromisoformat(data_inicio.replace('Z', '+00:00'))
                query = query.filter(Agendamento.data_hora >= data_inicio_dt)
            except ValueError:
                return jsonify({'erro': 'Formato de data_inicio inválido'}), 400
        
        if data_fim:
            try:
                data_fim_dt = datetime.fromisoformat(data_fim.replace('Z', '+00:00'))
                query = query.filter(Agendamento.data_hora <= data_fim_dt)
            except ValueError:
                return jsonify({'erro': 'Formato de data_fim inválido'}), 400
        
        agendamentos = query.order_by(Agendamento.data_hora).all()
        
        # Incluir informações do paciente
        agendamentos_dict = []
        for agendamento in agendamentos:
            agendamento_dict = agendamento.to_dict()
            agendamento_dict['paciente'] = agendamento.paciente.to_dict() if agendamento.paciente else None
            agendamentos_dict.append(agendamento_dict)
        
        return jsonify(agendamentos_dict)
    
    except Exception as e:
        return jsonify({'erro': str(e)}), 500

@agendamento_bp.route('/agendamentos', methods=['POST'])
def create_agendamento():
    """Criar novo agendamento"""
    try:
        data = request.json
        
        # Validações obrigatórias
        if not data.get('paciente_id'):
            return jsonify({'erro': 'Paciente é obrigatório'}), 400
        
        if not data.get('data_hora'):
            return jsonify({'erro': 'Data e hora são obrigatórias'}), 400
        
        # Verificar se o paciente existe
        paciente = Paciente.query.get(data['paciente_id'])
        if not paciente:
            return jsonify({'erro': 'Paciente não encontrado'}), 404
        
        # Converter data e hora
        try:
            data_hora = datetime.fromisoformat(data['data_hora'].replace('Z', '+00:00'))
        except ValueError:
            return jsonify({'erro': 'Formato de data/hora inválido'}), 400
        
        # Verificar se já existe agendamento no mesmo horário
        agendamento_existente = Agendamento.query.filter(
            Agendamento.data_hora == data_hora,
            Agendamento.status.in_(['agendado', 'confirmado'])
        ).first()
        
        if agendamento_existente:
            return jsonify({'erro': 'Já existe um agendamento para este horário'}), 409
        
        agendamento = Agendamento(
            paciente_id=data['paciente_id'],
            data_hora=data_hora,
            duracao_minutos=data.get('duracao_minutos', 60),
            status=data.get('status', 'agendado'),
            observacoes=data.get('observacoes')
        )
        
        db.session.add(agendamento)
        db.session.commit()
        
        # Incluir informações do paciente na resposta
        agendamento_dict = agendamento.to_dict()
        agendamento_dict['paciente'] = agendamento.paciente.to_dict()
        
        return jsonify(agendamento_dict), 201
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'erro': str(e)}), 500

@agendamento_bp.route('/agendamentos/<int:agendamento_id>', methods=['GET'])
def get_agendamento(agendamento_id):
    """Obter agendamento por ID"""
    try:
        agendamento = Agendamento.query.get_or_404(agendamento_id)
        
        # Incluir informações do paciente
        agendamento_dict = agendamento.to_dict()
        agendamento_dict['paciente'] = agendamento.paciente.to_dict()
        
        return jsonify(agendamento_dict)
    
    except Exception as e:
        return jsonify({'erro': str(e)}), 500

@agendamento_bp.route('/agendamentos/<int:agendamento_id>', methods=['PUT'])
def update_agendamento(agendamento_id):
    """Atualizar agendamento"""
    try:
        agendamento = Agendamento.query.get_or_404(agendamento_id)
        data = request.json
        
        # Atualizar campos
        if 'data_hora' in data:
            try:
                nova_data_hora = datetime.fromisoformat(data['data_hora'].replace('Z', '+00:00'))
                
                # Verificar se já existe agendamento no novo horário (exceto o atual)
                agendamento_existente = Agendamento.query.filter(
                    Agendamento.data_hora == nova_data_hora,
                    Agendamento.status.in_(['agendado', 'confirmado']),
                    Agendamento.id != agendamento_id
                ).first()
                
                if agendamento_existente:
                    return jsonify({'erro': 'Já existe um agendamento para este horário'}), 409
                
                agendamento.data_hora = nova_data_hora
            except ValueError:
                return jsonify({'erro': 'Formato de data/hora inválido'}), 400
        
        if 'duracao_minutos' in data:
            agendamento.duracao_minutos = data['duracao_minutos']
        
        if 'status' in data:
            agendamento.status = data['status']
        
        if 'observacoes' in data:
            agendamento.observacoes = data['observacoes']
        
        if 'lembrete_enviado' in data:
            agendamento.lembrete_enviado = data['lembrete_enviado']
        
        agendamento.data_atualizacao = datetime.utcnow()
        db.session.commit()
        
        # Incluir informações do paciente na resposta
        agendamento_dict = agendamento.to_dict()
        agendamento_dict['paciente'] = agendamento.paciente.to_dict()
        
        return jsonify(agendamento_dict)
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'erro': str(e)}), 500

@agendamento_bp.route('/agendamentos/<int:agendamento_id>', methods=['DELETE'])
def delete_agendamento(agendamento_id):
    """Cancelar agendamento"""
    try:
        agendamento = Agendamento.query.get_or_404(agendamento_id)
        
        # Marcar como cancelado em vez de excluir
        agendamento.status = 'cancelado'
        agendamento.data_atualizacao = datetime.utcnow()
        
        db.session.commit()
        
        return jsonify({'mensagem': 'Agendamento cancelado com sucesso'}), 200
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'erro': str(e)}), 500

@agendamento_bp.route('/agendamentos/calendario', methods=['GET'])
def get_calendario():
    """Obter agendamentos para visualização em calendário"""
    try:
        data_inicio = request.args.get('data_inicio')
        data_fim = request.args.get('data_fim')
        
        if not data_inicio or not data_fim:
            return jsonify({'erro': 'data_inicio e data_fim são obrigatórias'}), 400
        
        try:
            data_inicio_dt = datetime.fromisoformat(data_inicio.replace('Z', '+00:00'))
            data_fim_dt = datetime.fromisoformat(data_fim.replace('Z', '+00:00'))
        except ValueError:
            return jsonify({'erro': 'Formato de data inválido'}), 400
        
        agendamentos = Agendamento.query.filter(
            Agendamento.data_hora >= data_inicio_dt,
            Agendamento.data_hora <= data_fim_dt,
            Agendamento.status != 'cancelado'
        ).order_by(Agendamento.data_hora).all()
        
        # Formatar para calendário
        eventos = []
        for agendamento in agendamentos:
            evento = {
                'id': agendamento.id,
                'title': f"{agendamento.paciente.nome_completo}",
                'start': agendamento.data_hora.isoformat(),
                'end': (agendamento.data_hora + timedelta(minutes=agendamento.duracao_minutos)).isoformat(),
                'status': agendamento.status,
                'paciente_id': agendamento.paciente_id,
                'observacoes': agendamento.observacoes
            }
            eventos.append(evento)
        
        return jsonify(eventos)
    
    except Exception as e:
        return jsonify({'erro': str(e)}), 500

@agendamento_bp.route('/agendamentos/lembretes', methods=['POST'])
def enviar_lembretes():
    """Enviar lembretes para agendamentos do dia seguinte"""
    try:
        # Buscar agendamentos para o dia seguinte que ainda não tiveram lembrete enviado
        amanha = datetime.now().date() + timedelta(days=1)
        inicio_dia = datetime.combine(amanha, datetime.min.time())
        fim_dia = datetime.combine(amanha, datetime.max.time())
        
        agendamentos = Agendamento.query.filter(
            Agendamento.data_hora >= inicio_dia,
            Agendamento.data_hora <= fim_dia,
            Agendamento.status.in_(['agendado', 'confirmado']),
            Agendamento.lembrete_enviado == False
        ).all()
        
        lembretes_enviados = 0
        
        for agendamento in agendamentos:
            # TODO: Implementar envio real de e-mail/SMS
            # Por enquanto, apenas marcar como enviado
            
            # Verificar se o paciente tem consentimento para receber lembretes
            # TODO: Implementar campo de consentimento no modelo Paciente
            
            agendamento.lembrete_enviado = True
            lembretes_enviados += 1
        
        db.session.commit()
        
        return jsonify({
            'mensagem': f'{lembretes_enviados} lembretes enviados com sucesso',
            'total_enviados': lembretes_enviados
        })
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'erro': str(e)}), 500

