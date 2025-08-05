from flask import Blueprint, jsonify, request
from src.models.fisio_models import Avaliacao, Paciente, AnexoAvaliacao, db
from datetime import datetime
import json

avaliacao_bp = Blueprint('avaliacao', __name__)

@avaliacao_bp.route('/avaliacoes', methods=['GET'])
def get_avaliacoes():
    """Listar avaliações com filtros opcionais"""
    try:
        paciente_id = request.args.get('paciente_id', type=int)
        
        query = Avaliacao.query
        
        if paciente_id:
            query = query.filter(Avaliacao.paciente_id == paciente_id)
        
        avaliacoes = query.order_by(Avaliacao.data_avaliacao.desc()).all()
        return jsonify([avaliacao.to_dict() for avaliacao in avaliacoes])
    
    except Exception as e:
        return jsonify({'erro': str(e)}), 500

@avaliacao_bp.route('/avaliacoes', methods=['POST'])
def create_avaliacao():
    """Criar nova avaliação"""
    try:
        data = request.json
        
        # Validações obrigatórias
        if not data.get('paciente_id'):
            return jsonify({'erro': 'Paciente é obrigatório'}), 400
        
        # Verificar se o paciente existe
        paciente = Paciente.query.get(data['paciente_id'])
        if not paciente:
            return jsonify({'erro': 'Paciente não encontrado'}), 404
        
        # Converter data de avaliação se fornecida
        data_avaliacao = datetime.utcnow()
        if data.get('data_avaliacao'):
            try:
                data_avaliacao = datetime.fromisoformat(data['data_avaliacao'].replace('Z', '+00:00'))
            except ValueError:
                return jsonify({'erro': 'Formato de data inválido'}), 400
        
        # Validar e converter campos JSON da CIF
        funcoes_corpo = data.get('funcoes_corpo')
        if funcoes_corpo and isinstance(funcoes_corpo, dict):
            funcoes_corpo = json.dumps(funcoes_corpo)
        
        estruturas_corpo = data.get('estruturas_corpo')
        if estruturas_corpo and isinstance(estruturas_corpo, dict):
            estruturas_corpo = json.dumps(estruturas_corpo)
        
        atividades_participacao = data.get('atividades_participacao')
        if atividades_participacao and isinstance(atividades_participacao, dict):
            atividades_participacao = json.dumps(atividades_participacao)
        
        fatores_ambientais = data.get('fatores_ambientais')
        if fatores_ambientais and isinstance(fatores_ambientais, dict):
            fatores_ambientais = json.dumps(fatores_ambientais)
        
        avaliacao = Avaliacao(
            paciente_id=data['paciente_id'],
            data_avaliacao=data_avaliacao,
            queixa_principal=data.get('queixa_principal'),
            habitos_vida=data.get('habitos_vida'),
            historia_atual_doenca=data.get('historia_atual_doenca'),
            historia_pregressa_doenca=data.get('historia_pregressa_doenca'),
            antecedentes_pessoais=data.get('antecedentes_pessoais'),
            antecedentes_familiares=data.get('antecedentes_familiares'),
            tratamentos_realizados=data.get('tratamentos_realizados'),
            exame_clinico_fisico=data.get('exame_clinico_fisico'),
            exames_complementares=data.get('exames_complementares'),
            diagnostico_fisioterapeutico=data.get('diagnostico_fisioterapeutico'),
            prognostico_fisioterapeutico=data.get('prognostico_fisioterapeutico'),
            objetivos_terapeuticos=data.get('objetivos_terapeuticos'),
            recursos_metodos_tecnicas=data.get('recursos_metodos_tecnicas'),
            quantitativo_atendimentos=data.get('quantitativo_atendimentos'),
            funcoes_corpo=funcoes_corpo,
            estruturas_corpo=estruturas_corpo,
            atividades_participacao=atividades_participacao,
            fatores_ambientais=fatores_ambientais
        )
        
        db.session.add(avaliacao)
        db.session.commit()
        
        return jsonify(avaliacao.to_dict()), 201
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'erro': str(e)}), 500

@avaliacao_bp.route('/avaliacoes/<int:avaliacao_id>', methods=['GET'])
def get_avaliacao(avaliacao_id):
    """Obter avaliação por ID"""
    try:
        avaliacao = Avaliacao.query.get_or_404(avaliacao_id)
        
        # Incluir anexos na resposta
        avaliacao_dict = avaliacao.to_dict()
        avaliacao_dict['anexos'] = [anexo.to_dict() for anexo in avaliacao.anexos]
        
        # Converter campos JSON de volta para objetos
        if avaliacao.funcoes_corpo:
            try:
                avaliacao_dict['funcoes_corpo'] = json.loads(avaliacao.funcoes_corpo)
            except json.JSONDecodeError:
                pass
        
        if avaliacao.estruturas_corpo:
            try:
                avaliacao_dict['estruturas_corpo'] = json.loads(avaliacao.estruturas_corpo)
            except json.JSONDecodeError:
                pass
        
        if avaliacao.atividades_participacao:
            try:
                avaliacao_dict['atividades_participacao'] = json.loads(avaliacao.atividades_participacao)
            except json.JSONDecodeError:
                pass
        
        if avaliacao.fatores_ambientais:
            try:
                avaliacao_dict['fatores_ambientais'] = json.loads(avaliacao.fatores_ambientais)
            except json.JSONDecodeError:
                pass
        
        return jsonify(avaliacao_dict)
    
    except Exception as e:
        return jsonify({'erro': str(e)}), 500

@avaliacao_bp.route('/avaliacoes/<int:avaliacao_id>', methods=['PUT'])
def update_avaliacao(avaliacao_id):
    """Atualizar avaliação"""
    try:
        avaliacao = Avaliacao.query.get_or_404(avaliacao_id)
        data = request.json
        
        # Atualizar campos básicos
        campos_texto = [
            'queixa_principal', 'habitos_vida', 'historia_atual_doenca',
            'historia_pregressa_doenca', 'antecedentes_pessoais',
            'antecedentes_familiares', 'tratamentos_realizados',
            'exame_clinico_fisico', 'exames_complementares',
            'diagnostico_fisioterapeutico', 'prognostico_fisioterapeutico',
            'objetivos_terapeuticos', 'recursos_metodos_tecnicas'
        ]
        
        for campo in campos_texto:
            if campo in data:
                setattr(avaliacao, campo, data[campo])
        
        if 'quantitativo_atendimentos' in data:
            avaliacao.quantitativo_atendimentos = data['quantitativo_atendimentos']
        
        # Atualizar campos CIF
        campos_cif = ['funcoes_corpo', 'estruturas_corpo', 'atividades_participacao', 'fatores_ambientais']
        for campo in campos_cif:
            if campo in data:
                valor = data[campo]
                if isinstance(valor, dict):
                    valor = json.dumps(valor)
                setattr(avaliacao, campo, valor)
        
        if 'data_avaliacao' in data:
            try:
                avaliacao.data_avaliacao = datetime.fromisoformat(data['data_avaliacao'].replace('Z', '+00:00'))
            except ValueError:
                return jsonify({'erro': 'Formato de data inválido'}), 400
        
        avaliacao.data_atualizacao = datetime.utcnow()
        db.session.commit()
        
        return jsonify(avaliacao.to_dict())
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'erro': str(e)}), 500

@avaliacao_bp.route('/avaliacoes/<int:avaliacao_id>', methods=['DELETE'])
def delete_avaliacao(avaliacao_id):
    """Excluir avaliação"""
    try:
        avaliacao = Avaliacao.query.get_or_404(avaliacao_id)
        
        # Excluir anexos relacionados (cascade já configurado no modelo)
        db.session.delete(avaliacao)
        db.session.commit()
        
        return jsonify({'mensagem': 'Avaliação excluída com sucesso'}), 200
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'erro': str(e)}), 500

@avaliacao_bp.route('/avaliacoes/<int:avaliacao_id>/anexos', methods=['POST'])
def upload_anexo_avaliacao(avaliacao_id):
    """Upload de anexo para avaliação"""
    try:
        avaliacao = Avaliacao.query.get_or_404(avaliacao_id)
        
        # TODO: Implementar upload real para S3
        # Por enquanto, simular o upload
        data = request.json
        
        if not data.get('nome_arquivo'):
            return jsonify({'erro': 'Nome do arquivo é obrigatório'}), 400
        
        anexo = AnexoAvaliacao(
            avaliacao_id=avaliacao_id,
            nome_arquivo=data['nome_arquivo'],
            tipo_arquivo=data.get('tipo_arquivo'),
            tamanho_bytes=data.get('tamanho_bytes'),
            url_arquivo=data.get('url_arquivo'),
            categoria=data.get('categoria')
        )
        
        db.session.add(anexo)
        db.session.commit()
        
        return jsonify(anexo.to_dict()), 201
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'erro': str(e)}), 500

@avaliacao_bp.route('/avaliacoes/<int:avaliacao_id>/anexos/<int:anexo_id>', methods=['DELETE'])
def delete_anexo_avaliacao(avaliacao_id, anexo_id):
    """Excluir anexo de avaliação"""
    try:
        anexo = AnexoAvaliacao.query.filter_by(
            id=anexo_id, 
            avaliacao_id=avaliacao_id
        ).first_or_404()
        
        # TODO: Excluir arquivo do S3
        
        db.session.delete(anexo)
        db.session.commit()
        
        return jsonify({'mensagem': 'Anexo excluído com sucesso'}), 200
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'erro': str(e)}), 500

