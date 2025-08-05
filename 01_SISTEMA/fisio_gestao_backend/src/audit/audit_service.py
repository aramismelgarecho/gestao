from datetime import datetime
from flask import request
from src.models.fisio_models import db
from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean

class LogAuditoria(db.Model):
    """Modelo para logs de auditoria - LGPD compliance"""
    __tablename__ = 'logs_auditoria'
    
    id = Column(Integer, primary_key=True)
    fisioterapeuta_id = Column(Integer, db.ForeignKey('fisioterapeutas.id'), nullable=True)
    acao = Column(String(100), nullable=False)  # CREATE, READ, UPDATE, DELETE, LOGIN, LOGOUT
    tabela = Column(String(50), nullable=True)  # Nome da tabela afetada
    registro_id = Column(Integer, nullable=True)  # ID do registro afetado
    dados_anteriores = Column(Text, nullable=True)  # JSON dos dados antes da alteração
    dados_novos = Column(Text, nullable=True)  # JSON dos dados após a alteração
    ip_address = Column(String(45), nullable=True)  # IPv4 ou IPv6
    user_agent = Column(String(500), nullable=True)
    data_hora = Column(DateTime, default=datetime.utcnow, nullable=False)
    sucesso = Column(Boolean, default=True, nullable=False)
    observacoes = Column(Text, nullable=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'fisioterapeuta_id': self.fisioterapeuta_id,
            'acao': self.acao,
            'tabela': self.tabela,
            'registro_id': self.registro_id,
            'dados_anteriores': self.dados_anteriores,
            'dados_novos': self.dados_novos,
            'ip_address': self.ip_address,
            'user_agent': self.user_agent,
            'data_hora': self.data_hora.isoformat() if self.data_hora else None,
            'sucesso': self.sucesso,
            'observacoes': self.observacoes
        }

class AuditoriaService:
    @staticmethod
    def log_acao(acao, tabela=None, registro_id=None, dados_anteriores=None, 
                 dados_novos=None, fisioterapeuta_id=None, sucesso=True, observacoes=None):
        """Registrar ação no log de auditoria"""
        try:
            # Obter informações da requisição
            ip_address = request.remote_addr if request else None
            user_agent = request.headers.get('User-Agent') if request else None
            
            # Se fisioterapeuta_id não foi fornecido, tentar obter do contexto
            if not fisioterapeuta_id and hasattr(request, 'current_fisioterapeuta'):
                fisioterapeuta_id = request.current_fisioterapeuta.id
            
            log = LogAuditoria(
                fisioterapeuta_id=fisioterapeuta_id,
                acao=acao,
                tabela=tabela,
                registro_id=registro_id,
                dados_anteriores=dados_anteriores,
                dados_novos=dados_novos,
                ip_address=ip_address,
                user_agent=user_agent,
                sucesso=sucesso,
                observacoes=observacoes
            )
            
            db.session.add(log)
            db.session.commit()
            
        except Exception as e:
            # Em caso de erro no log, não deve afetar a operação principal
            print(f"Erro ao registrar log de auditoria: {str(e)}")
    
    @staticmethod
    def log_acesso_dados_pessoais(paciente_id, tipo_acesso, fisioterapeuta_id=None):
        """Log específico para acesso a dados pessoais - LGPD"""
        AuditoriaService.log_acao(
            acao='ACESSO_DADOS_PESSOAIS',
            tabela='pacientes',
            registro_id=paciente_id,
            fisioterapeuta_id=fisioterapeuta_id,
            observacoes=f'Tipo de acesso: {tipo_acesso}'
        )
    
    @staticmethod
    def log_exportacao_dados(paciente_id, formato, fisioterapeuta_id=None):
        """Log para exportação de dados - LGPD"""
        AuditoriaService.log_acao(
            acao='EXPORTACAO_DADOS',
            tabela='pacientes',
            registro_id=paciente_id,
            fisioterapeuta_id=fisioterapeuta_id,
            observacoes=f'Formato: {formato}'
        )
    
    @staticmethod
    def log_exclusao_dados(paciente_id, motivo, fisioterapeuta_id=None):
        """Log para exclusão de dados - LGPD"""
        AuditoriaService.log_acao(
            acao='EXCLUSAO_DADOS',
            tabela='pacientes',
            registro_id=paciente_id,
            fisioterapeuta_id=fisioterapeuta_id,
            observacoes=f'Motivo: {motivo}'
        )

def audit_decorator(acao, tabela=None):
    """Decorator para automatizar logs de auditoria"""
    def decorator(f):
        def wrapper(*args, **kwargs):
            import json
            
            # Executar função original
            try:
                resultado = f(*args, **kwargs)
                
                # Tentar extrair ID do resultado se for um objeto com to_dict
                registro_id = None
                dados_novos = None
                
                if hasattr(resultado, 'to_dict'):
                    dados_dict = resultado.to_dict()
                    registro_id = dados_dict.get('id')
                    dados_novos = json.dumps(dados_dict, default=str)
                elif isinstance(resultado, dict) and 'id' in resultado:
                    registro_id = resultado['id']
                    dados_novos = json.dumps(resultado, default=str)
                
                # Registrar log de sucesso
                AuditoriaService.log_acao(
                    acao=acao,
                    tabela=tabela,
                    registro_id=registro_id,
                    dados_novos=dados_novos,
                    sucesso=True
                )
                
                return resultado
                
            except Exception as e:
                # Registrar log de erro
                AuditoriaService.log_acao(
                    acao=acao,
                    tabela=tabela,
                    sucesso=False,
                    observacoes=f'Erro: {str(e)}'
                )
                raise e
        
        return wrapper
    return decorator

