from flask import Blueprint, request, jsonify
from src.models.user import db
from src.models.configuracoes import Categoria, Subcategoria
from sqlalchemy.exc import IntegrityError
from datetime import datetime

configuracoes_bp = Blueprint('configuracoes', __name__)

# ===== ROTAS PARA CATEGORIAS =====

@configuracoes_bp.route('/categorias', methods=['GET'])
def listar_categorias():
    """Lista todas as categorias ativas"""
    try:
        categorias = Categoria.query.filter_by(ativo=True).order_by(Categoria.nome).all()
        return jsonify({
            'success': True,
            'data': [categoria.to_dict() for categoria in categorias]
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Erro ao listar categorias: {str(e)}'
        }), 500

@configuracoes_bp.route('/categorias/<int:categoria_id>', methods=['GET'])
def obter_categoria(categoria_id):
    """Obtém uma categoria específica"""
    try:
        categoria = Categoria.query.get_or_404(categoria_id)
        return jsonify({
            'success': True,
            'data': categoria.to_dict()
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Erro ao obter categoria: {str(e)}'
        }), 500

@configuracoes_bp.route('/categorias', methods=['POST'])
def criar_categoria():
    """Cria uma nova categoria"""
    try:
        data = request.get_json()
        
        # Validação básica
        if not data or not data.get('nome'):
            return jsonify({
                'success': False,
                'message': 'Nome da categoria é obrigatório'
            }), 400
        
        # Padronização do nome (capitalizar primeira letra de cada palavra)
        nome_padronizado = data['nome'].strip().title()
        
        # Verificar se já existe
        categoria_existente = Categoria.query.filter_by(nome=nome_padronizado).first()
        if categoria_existente:
            return jsonify({
                'success': False,
                'message': f'Categoria "{nome_padronizado}" já existe'
            }), 409
        
        # Criar nova categoria
        nova_categoria = Categoria(
            nome=nome_padronizado,
            descricao=data.get('descricao', '').strip(),
            tipo=data.get('tipo', '').strip()
        )
        
        db.session.add(nova_categoria)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Categoria criada com sucesso',
            'data': nova_categoria.to_dict()
        }), 201
        
    except IntegrityError:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': 'Categoria já existe'
        }), 409
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'Erro ao criar categoria: {str(e)}'
        }), 500

@configuracoes_bp.route('/categorias/<int:categoria_id>', methods=['PUT'])
def atualizar_categoria(categoria_id):
    """Atualiza uma categoria existente"""
    try:
        categoria = Categoria.query.get_or_404(categoria_id)
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'message': 'Dados não fornecidos'
            }), 400
        
        # Atualizar campos se fornecidos
        if 'nome' in data:
            nome_padronizado = data['nome'].strip().title()
            # Verificar se o novo nome já existe (exceto para a própria categoria)
            categoria_existente = Categoria.query.filter(
                Categoria.nome == nome_padronizado,
                Categoria.id != categoria_id
            ).first()
            if categoria_existente:
                return jsonify({
                    'success': False,
                    'message': f'Categoria "{nome_padronizado}" já existe'
                }), 409
            categoria.nome = nome_padronizado
        
        if 'descricao' in data:
            categoria.descricao = data['descricao'].strip()
        
        if 'tipo' in data:
            categoria.tipo = data['tipo'].strip()
        
        categoria.data_atualizacao = datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Categoria atualizada com sucesso',
            'data': categoria.to_dict()
        }), 200
        
    except IntegrityError:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': 'Nome da categoria já existe'
        }), 409
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'Erro ao atualizar categoria: {str(e)}'
        }), 500

@configuracoes_bp.route('/categorias/<int:categoria_id>/arquivar', methods=['PUT'])
def arquivar_categoria(categoria_id):
    """Arquiva uma categoria (soft delete)"""
    try:
        categoria = Categoria.query.get_or_404(categoria_id)
        
        # Verificar se há subcategorias ativas
        subcategorias_ativas = Subcategoria.query.filter_by(
            categoria_id=categoria_id, 
            ativo=True
        ).count()
        
        if subcategorias_ativas > 0:
            return jsonify({
                'success': False,
                'message': f'Não é possível arquivar a categoria. Existem {subcategorias_ativas} subcategorias ativas.'
            }), 400
        
        categoria.ativo = False
        categoria.data_atualizacao = datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Categoria arquivada com sucesso'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'Erro ao arquivar categoria: {str(e)}'
        }), 500

# ===== ROTAS PARA SUBCATEGORIAS =====

@configuracoes_bp.route('/subcategorias', methods=['GET'])
def listar_subcategorias():
    """Lista todas as subcategorias ativas"""
    try:
        categoria_id = request.args.get('categoria_id')
        
        query = Subcategoria.query.filter_by(ativo=True)
        if categoria_id:
            query = query.filter_by(categoria_id=categoria_id)
        
        subcategorias = query.order_by(Subcategoria.nome).all()
        return jsonify({
            'success': True,
            'data': [subcategoria.to_dict() for subcategoria in subcategorias]
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Erro ao listar subcategorias: {str(e)}'
        }), 500

@configuracoes_bp.route('/subcategorias', methods=['POST'])
def criar_subcategoria():
    """Cria uma nova subcategoria"""
    try:
        data = request.get_json()
        
        # Validação básica
        if not data or not data.get('nome') or not data.get('categoria_id'):
            return jsonify({
                'success': False,
                'message': 'Nome da subcategoria e categoria são obrigatórios'
            }), 400
        
        # Verificar se a categoria existe
        categoria = Categoria.query.get(data['categoria_id'])
        if not categoria:
            return jsonify({
                'success': False,
                'message': 'Categoria não encontrada'
            }), 404
        
        # Padronização do nome
        nome_padronizado = data['nome'].strip().title()
        
        # Verificar se já existe subcategoria com mesmo nome na mesma categoria
        subcategoria_existente = Subcategoria.query.filter_by(
            nome=nome_padronizado,
            categoria_id=data['categoria_id']
        ).first()
        
        if subcategoria_existente:
            return jsonify({
                'success': False,
                'message': f'Subcategoria "{nome_padronizado}" já existe nesta categoria'
            }), 409
        
        # Criar nova subcategoria
        nova_subcategoria = Subcategoria(
            nome=nome_padronizado,
            descricao=data.get('descricao', '').strip(),
            categoria_id=data['categoria_id']
        )
        
        db.session.add(nova_subcategoria)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Subcategoria criada com sucesso',
            'data': nova_subcategoria.to_dict()
        }), 201
        
    except IntegrityError:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': 'Subcategoria já existe nesta categoria'
        }), 409
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'Erro ao criar subcategoria: {str(e)}'
        }), 500

@configuracoes_bp.route('/subcategorias/<int:subcategoria_id>', methods=['PUT'])
def atualizar_subcategoria(subcategoria_id):
    """Atualiza uma subcategoria existente"""
    try:
        subcategoria = Subcategoria.query.get_or_404(subcategoria_id)
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'message': 'Dados não fornecidos'
            }), 400
        
        # Atualizar campos se fornecidos
        if 'nome' in data:
            nome_padronizado = data['nome'].strip().title()
            # Verificar se o novo nome já existe na mesma categoria (exceto para a própria subcategoria)
            subcategoria_existente = Subcategoria.query.filter(
                Subcategoria.nome == nome_padronizado,
                Subcategoria.categoria_id == subcategoria.categoria_id,
                Subcategoria.id != subcategoria_id
            ).first()
            if subcategoria_existente:
                return jsonify({
                    'success': False,
                    'message': f'Subcategoria "{nome_padronizado}" já existe nesta categoria'
                }), 409
            subcategoria.nome = nome_padronizado
        
        if 'descricao' in data:
            subcategoria.descricao = data['descricao'].strip()
        
        subcategoria.data_atualizacao = datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Subcategoria atualizada com sucesso',
            'data': subcategoria.to_dict()
        }), 200
        
    except IntegrityError:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': 'Nome da subcategoria já existe nesta categoria'
        }), 409
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'Erro ao atualizar subcategoria: {str(e)}'
        }), 500

@configuracoes_bp.route('/subcategorias/<int:subcategoria_id>/arquivar', methods=['PUT'])
def arquivar_subcategoria(subcategoria_id):
    """Arquiva uma subcategoria (soft delete)"""
    try:
        subcategoria = Subcategoria.query.get_or_404(subcategoria_id)
        
        subcategoria.ativo = False
        subcategoria.data_atualizacao = datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Subcategoria arquivada com sucesso'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'Erro ao arquivar subcategoria: {str(e)}'
        }), 500

# ===== ROTAS AUXILIARES =====

@configuracoes_bp.route('/categorias/buscar', methods=['GET'])
def buscar_categorias():
    """Busca categorias por nome (para autocomplete)"""
    try:
        termo = request.args.get('q', '').strip()
        if not termo:
            return jsonify({
                'success': True,
                'data': []
            }), 200
        
        categorias = Categoria.query.filter(
            Categoria.nome.ilike(f'%{termo}%'),
            Categoria.ativo == True
        ).order_by(Categoria.nome).limit(10).all()
        
        return jsonify({
            'success': True,
            'data': [{'id': cat.id, 'nome': cat.nome} for cat in categorias]
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Erro na busca: {str(e)}'
        }), 500

@configuracoes_bp.route('/subcategorias/buscar', methods=['GET'])
def buscar_subcategorias():
    """Busca subcategorias por nome (para autocomplete)"""
    try:
        termo = request.args.get('q', '').strip()
        categoria_id = request.args.get('categoria_id')
        
        if not termo:
            return jsonify({
                'success': True,
                'data': []
            }), 200
        
        query = Subcategoria.query.filter(
            Subcategoria.nome.ilike(f'%{termo}%'),
            Subcategoria.ativo == True
        )
        
        if categoria_id:
            query = query.filter_by(categoria_id=categoria_id)
        
        subcategorias = query.order_by(Subcategoria.nome).limit(10).all()
        
        return jsonify({
            'success': True,
            'data': [{'id': sub.id, 'nome': sub.nome, 'categoria_id': sub.categoria_id} for sub in subcategorias]
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Erro na busca: {str(e)}'
        }), 500

