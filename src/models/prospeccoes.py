from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import json

# Usar a mesma instância db do user.py
from src.models.user import db

class Prospeccao(db.Model):
    __tablename__ = 'prospeccoes'
    
    id = db.Column(db.Integer, primary_key=True)
    numero_contrato = db.Column(db.String(10), unique=True, nullable=False)
    tipo_pessoa = db.Column(db.String(2), nullable=False)  # 'PF' ou 'PJ'
    cpf_cnpj = db.Column(db.String(18), nullable=False)
    nome_razao_social = db.Column(db.String(255), nullable=False)
    data_entrada = db.Column(db.Date, nullable=False)
    nome_responsavel = db.Column(db.String(255), nullable=False)
    celular = db.Column(db.String(20), nullable=False)
    email = db.Column(db.String(255), nullable=False)
    status_negociacao_id = db.Column(db.Integer, db.ForeignKey('categorias.id'), nullable=True)
    natureza_contrato_ids = db.Column(db.Text, nullable=True)  # JSON array
    followup_id = db.Column(db.Integer, db.ForeignKey('categorias.id'), nullable=True)
    total_linhas = db.Column(db.Integer, nullable=True)
    filiais = db.Column(db.Integer, nullable=True)
    cidade_id = db.Column(db.Integer, db.ForeignKey('categorias.id'), nullable=True)
    consultor_id = db.Column(db.Integer, db.ForeignKey('categorias.id'), nullable=True)
    data_aceite = db.Column(db.Date, nullable=True)
    tipo_aceite_id = db.Column(db.Integer, db.ForeignKey('categorias.id'), nullable=True)
    link_upload_aceite = db.Column(db.Text, nullable=True)
    descricao_tratativas = db.Column(db.Text, nullable=True)
    descricao_servicos = db.Column(db.Text, nullable=True)
    descricao_financeiro = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    arquivado = db.Column(db.Boolean, default=False)
    
    # Relacionamentos
    status_negociacao = db.relationship('Categoria', foreign_keys=[status_negociacao_id], backref='prospeccoes_status')
    followup = db.relationship('Categoria', foreign_keys=[followup_id], backref='prospeccoes_followup')
    cidade = db.relationship('Categoria', foreign_keys=[cidade_id], backref='prospeccoes_cidade')
    consultor = db.relationship('Categoria', foreign_keys=[consultor_id], backref='prospeccoes_consultor')
    tipo_aceite = db.relationship('Categoria', foreign_keys=[tipo_aceite_id], backref='prospeccoes_tipo_aceite')
    
    def __init__(self, **kwargs):
        super(Prospeccao, self).__init__(**kwargs)
        if not self.numero_contrato:
            self.numero_contrato = self.generate_numero_contrato()
    
    @staticmethod
    def generate_numero_contrato():
        """Gera o próximo número de contrato sequencial"""
        last_prospeccao = Prospeccao.query.order_by(Prospeccao.id.desc()).first()
        if last_prospeccao and last_prospeccao.numero_contrato:
            try:
                last_number = int(last_prospeccao.numero_contrato)
                next_number = last_number + 1
                return f"{next_number:04d}"
            except ValueError:
                pass
        return "0001"
    
    def get_natureza_contrato_ids(self):
        """Retorna a lista de IDs das naturezas do contrato"""
        if self.natureza_contrato_ids:
            try:
                return json.loads(self.natureza_contrato_ids)
            except json.JSONDecodeError:
                return []
        return []
    
    def set_natureza_contrato_ids(self, ids_list):
        """Define a lista de IDs das naturezas do contrato"""
        if ids_list:
            self.natureza_contrato_ids = json.dumps(ids_list)
        else:
            self.natureza_contrato_ids = None
    
    def to_dict(self):
        return {
            'id': self.id,
            'numero_contrato': self.numero_contrato,
            'tipo_pessoa': self.tipo_pessoa,
            'cpf_cnpj': self.cpf_cnpj,
            'nome_razao_social': self.nome_razao_social,
            'data_entrada': self.data_entrada.isoformat() if self.data_entrada else None,
            'nome_responsavel': self.nome_responsavel,
            'celular': self.celular,
            'email': self.email,
            'status_negociacao_id': self.status_negociacao_id,
            'status_negociacao': self.status_negociacao.to_dict() if self.status_negociacao else None,
            'natureza_contrato_ids': self.get_natureza_contrato_ids(),
            'followup_id': self.followup_id,
            'followup': self.followup.to_dict() if self.followup else None,
            'total_linhas': self.total_linhas,
            'filiais': self.filiais,
            'cidade_id': self.cidade_id,
            'cidade': self.cidade.to_dict() if self.cidade else None,
            'consultor_id': self.consultor_id,
            'consultor': self.consultor.to_dict() if self.consultor else None,
            'data_aceite': self.data_aceite.isoformat() if self.data_aceite else None,
            'tipo_aceite_id': self.tipo_aceite_id,
            'tipo_aceite': self.tipo_aceite.to_dict() if self.tipo_aceite else None,
            'link_upload_aceite': self.link_upload_aceite,
            'descricao_tratativas': self.descricao_tratativas,
            'descricao_servicos': self.descricao_servicos,
            'descricao_financeiro': self.descricao_financeiro,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'arquivado': self.arquivado
        }

