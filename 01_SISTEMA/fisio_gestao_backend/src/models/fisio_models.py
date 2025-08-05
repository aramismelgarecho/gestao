from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Fisioterapeuta(db.Model):
    """Modelo para fisioterapeutas do sistema"""
    __tablename__ = 'fisioterapeutas'
    
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(200), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    senha_hash = db.Column(db.LargeBinary, nullable=False)
    crefito = db.Column(db.String(20), unique=True, nullable=False)
    especialidade = db.Column(db.String(100))
    telefone = db.Column(db.String(20))
    is_admin = db.Column(db.Boolean, default=False)
    ativo = db.Column(db.Boolean, default=True)
    
    # Campos de segurança
    tentativas_login_falhadas = db.Column(db.Integer, default=0)
    conta_bloqueada = db.Column(db.Boolean, default=False)
    data_bloqueio = db.Column(db.DateTime)
    data_ultimo_login = db.Column(db.DateTime)
    data_ultima_tentativa_login = db.Column(db.DateTime)
    data_alteracao_senha = db.Column(db.DateTime)
    
    # Timestamps
    data_criacao = db.Column(db.DateTime, default=datetime.utcnow)
    data_atualizacao = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relacionamentos
    pacientes = db.relationship('Paciente', backref='fisioterapeuta', lazy=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'nome': self.nome,
            'email': self.email,
            'crefito': self.crefito,
            'especialidade': self.especialidade,
            'telefone': self.telefone,
            'is_admin': self.is_admin,
            'ativo': self.ativo,
            'data_ultimo_login': self.data_ultimo_login.isoformat() if self.data_ultimo_login else None,
            'data_criacao': self.data_criacao.isoformat() if self.data_criacao else None,
            'data_atualizacao': self.data_atualizacao.isoformat() if self.data_atualizacao else None
        }

class Paciente(db.Model):
    """Modelo para pacientes"""
    __tablename__ = 'pacientes'
    
    id = db.Column(db.Integer, primary_key=True)
    fisioterapeuta_id = db.Column(db.Integer, db.ForeignKey('fisioterapeutas.id'), nullable=False)
    
    # Dados pessoais básicos (COFFITO)
    nome_completo = db.Column(db.String(200), nullable=False)
    data_nascimento = db.Column(db.Date, nullable=False)
    genero = db.Column(db.String(20))
    estado_civil = db.Column(db.String(20))
    profissao = db.Column(db.String(100))
    naturalidade = db.Column(db.String(100))
    local_nascimento = db.Column(db.String(200))
    
    # Dados de contato
    telefone = db.Column(db.String(20))
    email = db.Column(db.String(120))
    endereco_residencial = db.Column(db.Text)
    endereco_comercial = db.Column(db.Text)
    
    # Campos de controle
    ativo = db.Column(db.Boolean, default=True)
    arquivado = db.Column(db.Boolean, default=False)
    
    # Campos LGPD
    consentimento_tratamento_dados = db.Column(db.Boolean, default=True)
    consentimento_comunicacao = db.Column(db.Boolean, default=False)
    consentimento_pesquisa = db.Column(db.Boolean, default=False)
    data_consentimento = db.Column(db.DateTime)
    versao_termos = db.Column(db.String(10), default='1.0')
    data_exclusao_lgpd = db.Column(db.DateTime)
    motivo_exclusao_lgpd = db.Column(db.Text)
    
    # Timestamps
    data_criacao = db.Column(db.DateTime, default=datetime.utcnow)
    data_atualizacao = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relacionamentos
    avaliacoes = db.relationship('Avaliacao', backref='paciente', lazy=True, cascade='all, delete-orphan')
    evolucoes = db.relationship('Evolucao', backref='paciente', lazy=True, cascade='all, delete-orphan')
    agendamentos = db.relationship('Agendamento', backref='paciente', lazy=True, cascade='all, delete-orphan')
    
    def to_dict(self):
        return {
            'id': self.id,
            'fisioterapeuta_id': self.fisioterapeuta_id,
            'nome_completo': self.nome_completo,
            'data_nascimento': self.data_nascimento.isoformat() if self.data_nascimento else None,
            'genero': self.genero,
            'estado_civil': self.estado_civil,
            'profissao': self.profissao,
            'naturalidade': self.naturalidade,
            'local_nascimento': self.local_nascimento,
            'telefone': self.telefone,
            'email': self.email,
            'endereco_residencial': self.endereco_residencial,
            'endereco_comercial': self.endereco_comercial,
            'ativo': self.ativo,
            'arquivado': self.arquivado,
            'consentimento_tratamento_dados': self.consentimento_tratamento_dados,
            'consentimento_comunicacao': self.consentimento_comunicacao,
            'consentimento_pesquisa': self.consentimento_pesquisa,
            'data_consentimento': self.data_consentimento.isoformat() if self.data_consentimento else None,
            'versao_termos': self.versao_termos,
            'data_criacao': self.data_criacao.isoformat() if self.data_criacao else None,
            'data_atualizacao': self.data_atualizacao.isoformat() if self.data_atualizacao else None
        }

class Avaliacao(db.Model):
    """Modelo para avaliações fisioterapêuticas baseadas na CIF"""
    __tablename__ = 'avaliacoes'
    
    id = db.Column(db.Integer, primary_key=True)
    
    # História clínica (conforme COFFITO)
    queixa_principal = db.Column(db.Text)
    habitos_vida = db.Column(db.Text)
    historia_atual_doenca = db.Column(db.Text)
    historia_pregressa_doenca = db.Column(db.Text)
    antecedentes_pessoais = db.Column(db.Text)
    antecedentes_familiares = db.Column(db.Text)
    tratamentos_realizados = db.Column(db.Text)
    
    # Exame clínico/físico
    exame_clinico_fisico = db.Column(db.Text)
    exames_complementares = db.Column(db.Text)
    
    # Diagnóstico e prognóstico fisioterapêuticos
    diagnostico_fisioterapeutico = db.Column(db.Text)
    prognostico_fisioterapeutico = db.Column(db.Text)
    
    # Plano terapêutico
    objetivos_terapeuticos = db.Column(db.Text)
    recursos_metodos_tecnicas = db.Column(db.Text)
    quantitativo_atendimentos = db.Column(db.Integer)
    
    # Campos baseados na CIF
    funcoes_corpo = db.Column(db.Text)  # JSON com avaliação das funções do corpo
    estruturas_corpo = db.Column(db.Text)  # JSON com avaliação das estruturas do corpo
    atividades_participacao = db.Column(db.Text)  # JSON com avaliação de atividades e participação
    fatores_ambientais = db.Column(db.Text)  # JSON com fatores ambientais
    
    # Campos de controle
    data_avaliacao = db.Column(db.DateTime, default=datetime.utcnow)
    data_criacao = db.Column(db.DateTime, default=datetime.utcnow)
    data_atualizacao = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relacionamentos
    paciente_id = db.Column(db.Integer, db.ForeignKey('pacientes.id'), nullable=False)
    evolucoes = db.relationship('Evolucao', backref='avaliacao', lazy=True)
    anexos = db.relationship('AnexoAvaliacao', backref='avaliacao', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Avaliacao {self.id} - Paciente {self.paciente_id}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'queixa_principal': self.queixa_principal,
            'habitos_vida': self.habitos_vida,
            'historia_atual_doenca': self.historia_atual_doenca,
            'historia_pregressa_doenca': self.historia_pregressa_doenca,
            'antecedentes_pessoais': self.antecedentes_pessoais,
            'antecedentes_familiares': self.antecedentes_familiares,
            'tratamentos_realizados': self.tratamentos_realizados,
            'exame_clinico_fisico': self.exame_clinico_fisico,
            'exames_complementares': self.exames_complementares,
            'diagnostico_fisioterapeutico': self.diagnostico_fisioterapeutico,
            'prognostico_fisioterapeutico': self.prognostico_fisioterapeutico,
            'objetivos_terapeuticos': self.objetivos_terapeuticos,
            'recursos_metodos_tecnicas': self.recursos_metodos_tecnicas,
            'quantitativo_atendimentos': self.quantitativo_atendimentos,
            'funcoes_corpo': self.funcoes_corpo,
            'estruturas_corpo': self.estruturas_corpo,
            'atividades_participacao': self.atividades_participacao,
            'fatores_ambientais': self.fatores_ambientais,
            'data_avaliacao': self.data_avaliacao.isoformat() if self.data_avaliacao else None,
            'data_criacao': self.data_criacao.isoformat() if self.data_criacao else None,
            'data_atualizacao': self.data_atualizacao.isoformat() if self.data_atualizacao else None,
            'paciente_id': self.paciente_id
        }

class Evolucao(db.Model):
    """Modelo para evoluções por sessão"""
    __tablename__ = 'evolucoes'
    
    id = db.Column(db.Integer, primary_key=True)
    data_sessao = db.Column(db.DateTime, nullable=False)
    procedimentos_realizados = db.Column(db.Text)
    resposta_paciente = db.Column(db.Text)
    intercorrencias = db.Column(db.Text)
    observacoes = db.Column(db.Text)
    
    # Campos de controle
    data_criacao = db.Column(db.DateTime, default=datetime.utcnow)
    data_atualizacao = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relacionamentos
    paciente_id = db.Column(db.Integer, db.ForeignKey('pacientes.id'), nullable=False)
    avaliacao_id = db.Column(db.Integer, db.ForeignKey('avaliacoes.id'))
    procedimentos = db.relationship('ProcedimentoEvolucao', backref='evolucao', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Evolucao {self.id} - Paciente {self.paciente_id}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'data_sessao': self.data_sessao.isoformat() if self.data_sessao else None,
            'procedimentos_realizados': self.procedimentos_realizados,
            'resposta_paciente': self.resposta_paciente,
            'intercorrencias': self.intercorrencias,
            'observacoes': self.observacoes,
            'data_criacao': self.data_criacao.isoformat() if self.data_criacao else None,
            'data_atualizacao': self.data_atualizacao.isoformat() if self.data_atualizacao else None,
            'paciente_id': self.paciente_id,
            'avaliacao_id': self.avaliacao_id
        }

class Procedimento(db.Model):
    """Catálogo de procedimentos fisioterapêuticos"""
    __tablename__ = 'procedimentos'
    
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(200), nullable=False)
    descricao = db.Column(db.Text)
    duracao_minutos = db.Column(db.Integer)
    codigo = db.Column(db.String(50))  # Código do procedimento, se aplicável
    ativo = db.Column(db.Boolean, default=True, nullable=False)
    
    # Campos de controle
    data_criacao = db.Column(db.DateTime, default=datetime.utcnow)
    data_atualizacao = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<Procedimento {self.nome}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'nome': self.nome,
            'descricao': self.descricao,
            'duracao_minutos': self.duracao_minutos,
            'codigo': self.codigo,
            'ativo': self.ativo,
            'data_criacao': self.data_criacao.isoformat() if self.data_criacao else None,
            'data_atualizacao': self.data_atualizacao.isoformat() if self.data_atualizacao else None
        }

class ProcedimentoEvolucao(db.Model):
    """Relacionamento entre procedimentos e evoluções"""
    __tablename__ = 'procedimentos_evolucoes'
    
    id = db.Column(db.Integer, primary_key=True)
    evolucao_id = db.Column(db.Integer, db.ForeignKey('evolucoes.id'), nullable=False)
    procedimento_id = db.Column(db.Integer, db.ForeignKey('procedimentos.id'), nullable=False)
    observacoes = db.Column(db.Text)
    
    # Relacionamentos
    procedimento = db.relationship('Procedimento', backref='evolucoes_procedimentos')
    
    def to_dict(self):
        return {
            'id': self.id,
            'evolucao_id': self.evolucao_id,
            'procedimento_id': self.procedimento_id,
            'observacoes': self.observacoes,
            'procedimento': self.procedimento.to_dict() if self.procedimento else None
        }

class AnexoAvaliacao(db.Model):
    """Anexos de avaliações (exames, imagens, etc.)"""
    __tablename__ = 'anexos_avaliacoes'
    
    id = db.Column(db.Integer, primary_key=True)
    nome_arquivo = db.Column(db.String(255), nullable=False)
    tipo_arquivo = db.Column(db.String(50))  # image, pdf, video, etc.
    tamanho_bytes = db.Column(db.Integer)
    url_arquivo = db.Column(db.String(500))  # URL do arquivo no S3 ou caminho local
    categoria = db.Column(db.String(100))  # Exames de Imagem, Fotos de Evolução, etc.
    
    # Campos de controle
    data_upload = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relacionamentos
    avaliacao_id = db.Column(db.Integer, db.ForeignKey('avaliacoes.id'), nullable=False)
    
    def __repr__(self):
        return f'<AnexoAvaliacao {self.nome_arquivo}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'nome_arquivo': self.nome_arquivo,
            'tipo_arquivo': self.tipo_arquivo,
            'tamanho_bytes': self.tamanho_bytes,
            'url_arquivo': self.url_arquivo,
            'categoria': self.categoria,
            'data_upload': self.data_upload.isoformat() if self.data_upload else None,
            'avaliacao_id': self.avaliacao_id
        }

class Agendamento(db.Model):
    """Agendamentos de sessões"""
    __tablename__ = 'agendamentos'
    
    id = db.Column(db.Integer, primary_key=True)
    data_hora = db.Column(db.DateTime, nullable=False)
    duracao_minutos = db.Column(db.Integer, default=60)
    status = db.Column(db.String(20), default='agendado')  # agendado, confirmado, realizado, cancelado
    observacoes = db.Column(db.Text)
    lembrete_enviado = db.Column(db.Boolean, default=False)
    
    # Campos de controle
    data_criacao = db.Column(db.DateTime, default=datetime.utcnow)
    data_atualizacao = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relacionamentos
    paciente_id = db.Column(db.Integer, db.ForeignKey('pacientes.id'), nullable=False)
    
    def __repr__(self):
        return f'<Agendamento {self.id} - {self.data_hora}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'data_hora': self.data_hora.isoformat() if self.data_hora else None,
            'duracao_minutos': self.duracao_minutos,
            'status': self.status,
            'observacoes': self.observacoes,
            'lembrete_enviado': self.lembrete_enviado,
            'data_criacao': self.data_criacao.isoformat() if self.data_criacao else None,
            'data_atualizacao': self.data_atualizacao.isoformat() if self.data_atualizacao else None,
            'paciente_id': self.paciente_id
        }

