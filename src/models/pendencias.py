from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

# Usar a mesma instância db do user.py
from src.models.user import db

class Pendencia(db.Model):
    __tablename__ = 'pendencias'
    
    id = db.Column(db.Integer, primary_key=True)
    data_entrada = db.Column(db.Date, default=datetime.utcnow().date())
    data_prevista = db.Column(db.Date, nullable=False)
    data_finalizacao = db.Column(db.Date, nullable=True)
    status_pendencia_id = db.Column(db.Integer, db.ForeignKey('categorias.id'), nullable=True)
    cliente_id = db.Column(db.Integer, db.ForeignKey('clientes.id'), nullable=True)
    aba_mae = db.Column(db.String(50), nullable=False)  # Ex: 'prospeccoes', 'contratos'
    aba_principal = db.Column(db.String(50), nullable=False)  # Ex: 'clientes', 'filiais'
    colaborador_id = db.Column(db.Integer, db.ForeignKey('categorias.id'), nullable=True)
    descricao = db.Column(db.Text, nullable=False)
    visto_gerencia = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    arquivado = db.Column(db.Boolean, default=False)
    
    # Relacionamentos
    status_pendencia = db.relationship('Categoria', foreign_keys=[status_pendencia_id], backref='pendencias_status')
    cliente = db.relationship('Cliente', backref='pendencias')
    colaborador = db.relationship('Categoria', foreign_keys=[colaborador_id], backref='pendencias_colaborador')
    
    def to_dict(self):
        return {
            'id': self.id,
            'data_entrada': self.data_entrada.isoformat() if self.data_entrada else None,
            'data_prevista': self.data_prevista.isoformat() if self.data_prevista else None,
            'data_finalizacao': self.data_finalizacao.isoformat() if self.data_finalizacao else None,
            'status_pendencia_id': self.status_pendencia_id,
            'status_pendencia': self.status_pendencia.to_dict() if self.status_pendencia else None,
            'cliente_id': self.cliente_id,
            'cliente': self.cliente.to_dict() if self.cliente else None,
            'aba_mae': self.aba_mae,
            'aba_principal': self.aba_principal,
            'colaborador_id': self.colaborador_id,
            'colaborador': self.colaborador.to_dict() if self.colaborador else None,
            'descricao': self.descricao,
            'visto_gerencia': self.visto_gerencia,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'arquivado': self.arquivado
        }
