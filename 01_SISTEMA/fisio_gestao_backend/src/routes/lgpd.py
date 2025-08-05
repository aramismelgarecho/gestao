from flask import Blueprint, jsonify, request, send_file
from datetime import datetime
import json
import io
import csv
from src.models.fisio_models import Paciente, Avaliacao, Evolucao, Agendamento, db
from src.audit.audit_service import AuditoriaService
from src.auth.auth_service import token_required

lgpd_bp = Blueprint('lgpd', __name__)

@lgpd_bp.route('/lgpd/consentimento/<int:paciente_id>', methods=['POST'])
@token_required
def registrar_consentimento(paciente_id):
    """Registrar consentimento do paciente para tratamento de dados"""
    try:
        data = request.json
        paciente = Paciente.query.get_or_404(paciente_id)
        
        # Atualizar campos de consentimento
        paciente.consentimento_tratamento_dados = data.get('consentimento_tratamento_dados', True)
        paciente.consentimento_comunicacao = data.get('consentimento_comunicacao', False)
        paciente.consentimento_pesquisa = data.get('consentimento_pesquisa', False)
        paciente.data_consentimento = datetime.utcnow()
        paciente.versao_termos = data.get('versao_termos', '1.0')
        
        db.session.commit()
        
        # Log de auditoria
        AuditoriaService.log_acao(
            acao='CONSENTIMENTO_ATUALIZADO',
            tabela='pacientes',
            registro_id=paciente_id,
            dados_novos=json.dumps({
                'consentimento_tratamento_dados': paciente.consentimento_tratamento_dados,
                'consentimento_comunicacao': paciente.consentimento_comunicacao,
                'consentimento_pesquisa': paciente.consentimento_pesquisa,
                'versao_termos': paciente.versao_termos
            })
        )
        
        return jsonify({
            'mensagem': 'Consentimento registrado com sucesso',
            'data_consentimento': paciente.data_consentimento.isoformat()
        })
    
    except Exception as e:
        return jsonify({'erro': str(e)}), 500

@lgpd_bp.route('/lgpd/portabilidade/<int:paciente_id>', methods=['GET'])
@token_required
def exportar_dados_paciente(paciente_id):
    """Exportar todos os dados do paciente - Direito à portabilidade (LGPD)"""
    try:
        formato = request.args.get('formato', 'json')  # json ou csv
        
        paciente = Paciente.query.get_or_404(paciente_id)
        
        # Coletar todos os dados do paciente
        dados_paciente = {
            'informacoes_pessoais': paciente.to_dict(),
            'avaliacoes': [av.to_dict() for av in paciente.avaliacoes],
            'evolucoes': [ev.to_dict() for ev in paciente.evolucoes],
            'agendamentos': [ag.to_dict() for ag in paciente.agendamentos]
        }
        
        # Log de auditoria
        AuditoriaService.log_exportacao_dados(
            paciente_id=paciente_id,
            formato=formato
        )
        
        if formato == 'csv':
            # Exportar como CSV
            output = io.StringIO()
            
            # Informações pessoais
            writer = csv.writer(output)
            writer.writerow(['INFORMAÇÕES PESSOAIS'])
            writer.writerow(['Campo', 'Valor'])
            
            for key, value in dados_paciente['informacoes_pessoais'].items():
                writer.writerow([key, value])
            
            writer.writerow([])  # Linha vazia
            
            # Avaliações
            if dados_paciente['avaliacoes']:
                writer.writerow(['AVALIAÇÕES'])
                if dados_paciente['avaliacoes']:
                    headers = list(dados_paciente['avaliacoes'][0].keys())
                    writer.writerow(headers)
                    for avaliacao in dados_paciente['avaliacoes']:
                        writer.writerow([avaliacao.get(h, '') for h in headers])
            
            writer.writerow([])  # Linha vazia
            
            # Evoluções
            if dados_paciente['evolucoes']:
                writer.writerow(['EVOLUÇÕES'])
                if dados_paciente['evolucoes']:
                    headers = list(dados_paciente['evolucoes'][0].keys())
                    writer.writerow(headers)
                    for evolucao in dados_paciente['evolucoes']:
                        writer.writerow([evolucao.get(h, '') for h in headers])
            
            output.seek(0)
            
            return send_file(
                io.BytesIO(output.getvalue().encode('utf-8')),
                mimetype='text/csv',
                as_attachment=True,
                download_name=f'dados_paciente_{paciente_id}_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
            )
        
        else:
            # Exportar como JSON
            return jsonify({
                'paciente_id': paciente_id,
                'data_exportacao': datetime.utcnow().isoformat(),
                'dados': dados_paciente
            })
    
    except Exception as e:
        return jsonify({'erro': str(e)}), 500

@lgpd_bp.route('/lgpd/esquecimento/<int:paciente_id>', methods=['DELETE'])
@token_required
def direito_esquecimento(paciente_id):
    """Implementar direito ao esquecimento - LGPD"""
    try:
        data = request.json
        motivo = data.get('motivo', 'Solicitação do titular dos dados')
        
        paciente = Paciente.query.get_or_404(paciente_id)
        
        # Verificar se há impedimentos legais para exclusão
        # (ex: processos judiciais, obrigações fiscais, etc.)
        impedimentos = []
        
        # Verificar agendamentos futuros
        agendamentos_futuros = Agendamento.query.filter(
            Agendamento.paciente_id == paciente_id,
            Agendamento.data_hora > datetime.utcnow(),
            Agendamento.status.in_(['agendado', 'confirmado'])
        ).count()
        
        if agendamentos_futuros > 0:
            impedimentos.append(f'{agendamentos_futuros} agendamento(s) futuro(s)')
        
        # Se há impedimentos, retornar erro
        if impedimentos:
            return jsonify({
                'erro': 'Não é possível excluir os dados devido a impedimentos legais',
                'impedimentos': impedimentos
            }), 400
        
        # Backup dos dados antes da exclusão (para auditoria)
        dados_backup = {
            'paciente': paciente.to_dict(),
            'avaliacoes': [av.to_dict() for av in paciente.avaliacoes],
            'evolucoes': [ev.to_dict() for ev in paciente.evolucoes],
            'agendamentos': [ag.to_dict() for ag in paciente.agendamentos]
        }
        
        # Log de auditoria antes da exclusão
        AuditoriaService.log_exclusao_dados(
            paciente_id=paciente_id,
            motivo=motivo
        )
        
        # Anonizar dados em vez de excluir completamente (para manter integridade referencial)
        paciente.nome_completo = f"[REMOVIDO_{paciente_id}]"
        paciente.email = None
        paciente.telefone = None
        paciente.endereco_residencial = None
        paciente.endereco_comercial = None
        paciente.profissao = None
        paciente.naturalidade = None
        paciente.local_nascimento = None
        paciente.ativo = False
        paciente.arquivado = True
        paciente.data_exclusao_lgpd = datetime.utcnow()
        paciente.motivo_exclusao_lgpd = motivo
        
        # Anonizar dados em avaliações
        for avaliacao in paciente.avaliacoes:
            avaliacao.queixa_principal = "[DADOS REMOVIDOS]"
            avaliacao.historia_doenca_atual = "[DADOS REMOVIDOS]"
            avaliacao.historia_patologica_pregressa = "[DADOS REMOVIDOS]"
            avaliacao.historia_familiar = "[DADOS REMOVIDOS]"
            avaliacao.historia_social = "[DADOS REMOVIDOS]"
            avaliacao.observacoes = "[DADOS REMOVIDOS]"
        
        # Anonizar dados em evoluções
        for evolucao in paciente.evolucoes:
            evolucao.procedimentos_realizados = "[DADOS REMOVIDOS]"
            evolucao.resposta_paciente = "[DADOS REMOVIDOS]"
            evolucao.intercorrencias = "[DADOS REMOVIDOS]"
            evolucao.observacoes = "[DADOS REMOVIDOS]"
        
        db.session.commit()
        
        return jsonify({
            'mensagem': 'Dados anonimizados com sucesso conforme LGPD',
            'data_exclusao': paciente.data_exclusao_lgpd.isoformat(),
            'motivo': motivo
        })
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'erro': str(e)}), 500

@lgpd_bp.route('/lgpd/retificacao/<int:paciente_id>', methods=['PUT'])
@token_required
def retificar_dados(paciente_id):
    """Permitir retificação de dados pessoais - LGPD"""
    try:
        data = request.json
        paciente = Paciente.query.get_or_404(paciente_id)
        
        # Backup dos dados anteriores
        dados_anteriores = paciente.to_dict()
        
        # Campos que podem ser retificados pelo próprio paciente
        campos_permitidos = [
            'nome_completo', 'email', 'telefone', 'endereco_residencial',
            'endereco_comercial', 'profissao', 'estado_civil'
        ]
        
        alteracoes = {}
        for campo in campos_permitidos:
            if campo in data:
                valor_anterior = getattr(paciente, campo)
                valor_novo = data[campo]
                
                if valor_anterior != valor_novo:
                    setattr(paciente, campo, valor_novo)
                    alteracoes[campo] = {
                        'anterior': valor_anterior,
                        'novo': valor_novo
                    }
        
        if alteracoes:
            paciente.data_atualizacao = datetime.utcnow()
            db.session.commit()
            
            # Log de auditoria
            AuditoriaService.log_acao(
                acao='RETIFICACAO_DADOS',
                tabela='pacientes',
                registro_id=paciente_id,
                dados_anteriores=json.dumps(dados_anteriores, default=str),
                dados_novos=json.dumps(paciente.to_dict(), default=str),
                observacoes=f'Campos alterados: {", ".join(alteracoes.keys())}'
            )
            
            return jsonify({
                'mensagem': 'Dados retificados com sucesso',
                'alteracoes': alteracoes
            })
        else:
            return jsonify({'mensagem': 'Nenhuma alteração detectada'})
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'erro': str(e)}), 500

@lgpd_bp.route('/lgpd/relatorio-tratamento/<int:paciente_id>', methods=['GET'])
@token_required
def relatorio_tratamento_dados(paciente_id):
    """Gerar relatório de tratamento de dados do paciente - LGPD"""
    try:
        paciente = Paciente.query.get_or_404(paciente_id)
        
        # Buscar logs de auditoria relacionados ao paciente
        logs = db.session.query(LogAuditoria).filter(
            LogAuditoria.registro_id == paciente_id,
            LogAuditoria.tabela == 'pacientes'
        ).order_by(LogAuditoria.data_hora.desc()).all()
        
        relatorio = {
            'paciente_id': paciente_id,
            'nome': paciente.nome_completo,
            'data_cadastro': paciente.data_criacao.isoformat() if paciente.data_criacao else None,
            'consentimento': {
                'tratamento_dados': paciente.consentimento_tratamento_dados,
                'comunicacao': paciente.consentimento_comunicacao,
                'pesquisa': paciente.consentimento_pesquisa,
                'data_consentimento': paciente.data_consentimento.isoformat() if paciente.data_consentimento else None,
                'versao_termos': paciente.versao_termos
            },
            'finalidades_tratamento': [
                'Prestação de serviços fisioterapêuticos',
                'Acompanhamento do tratamento',
                'Comunicação sobre agendamentos',
                'Cumprimento de obrigações legais (COFFITO)'
            ],
            'base_legal': 'Execução de contrato (Art. 7º, V da LGPD)',
            'dados_coletados': [
                'Dados pessoais básicos',
                'Dados de saúde',
                'Dados de contato',
                'Histórico de tratamentos'
            ],
            'compartilhamento': 'Dados não são compartilhados com terceiros',
            'retencao': 'Dados mantidos pelo prazo legal de 20 anos (CFM)',
            'historico_acessos': [log.to_dict() for log in logs[:50]]  # Últimos 50 logs
        }
        
        # Log do acesso ao relatório
        AuditoriaService.log_acao(
            acao='RELATORIO_TRATAMENTO_DADOS',
            tabela='pacientes',
            registro_id=paciente_id
        )
        
        return jsonify(relatorio)
    
    except Exception as e:
        return jsonify({'erro': str(e)}), 500

