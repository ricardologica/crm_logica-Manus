from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

# Usar a mesma instância db do user.py
from src.models.user import db

class Categoria(db.Model):
    __tablename__ = 'categorias'
    
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False, unique=True)
    descricao = db.Column(db.Text)
    tipo = db.Column(db.String(50))  # Para identificar o contexto (ex: 'propostas', 'clientes', 'linhas', etc.)
    ativo = db.Column(db.Boolean, default=True, nullable=False)
    data_criacao = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    data_atualizacao = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relacionamento com subcategorias
    subcategorias = db.relationship('Subcategoria', backref='categoria', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Categoria {self.nome}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'nome': self.nome,
            'descricao': self.descricao,
            'tipo': self.tipo,
            'ativo': self.ativo,
            'data_criacao': self.data_criacao.isoformat() if self.data_criacao else None,
            'data_atualizacao': self.data_atualizacao.isoformat() if self.data_atualizacao else None,
            'subcategorias': [sub.to_dict() for sub in self.subcategorias if sub.ativo]
        }

class Subcategoria(db.Model):
    __tablename__ = 'subcategorias'
    
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    descricao = db.Column(db.Text)
    categoria_id = db.Column(db.Integer, db.ForeignKey('categorias.id'), nullable=False)
    ativo = db.Column(db.Boolean, default=True, nullable=False)
    data_criacao = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    data_atualizacao = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Constraint para evitar duplicação de subcategorias dentro da mesma categoria
    __table_args__ = (db.UniqueConstraint('nome', 'categoria_id', name='unique_subcategoria_por_categoria'),)
    
    def __repr__(self):
        return f'<Subcategoria {self.nome}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'nome': self.nome,
            'descricao': self.descricao,
            'categoria_id': self.categoria_id,
            'categoria_nome': self.categoria.nome if self.categoria else None,
            'ativo': self.ativo,
            'data_criacao': self.data_criacao.isoformat() if self.data_criacao else None,
            'data_atualizacao': self.data_atualizacao.isoformat() if self.data_atualizacao else None
        }

