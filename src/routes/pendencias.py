from flask import Blueprint, request, jsonify
from src.models.user import db
from src.models.pendencias import Pendencia
from src.models.configuracoes import Categoria
from sqlalchemy.exc import IntegrityError
from datetime import datetime, timedelta

pendencias_bp = Blueprint('pendencias', __name__)

@pendencias_bp.route('/api/pendencias', methods=['GET'])
def get_pendencias():
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        search = request.args.get('search', '')
        arquivado = request.args.get('arquivado', 'false').lower() == 'true'
        
        query = Pendencia.query.filter_by(arquivado=arquivado)
        
        if search:
            query = query.filter(
                db.or_(
                    Pendencia.descricao.contains(search),
                    Pendencia.aba_mae.contains(search),
                    Pendencia.aba_principal.contains(search)
                )
            )
        
        pendencias = query.order_by(Pendencia.data_prevista.asc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        return jsonify({
            'pendencias': [pendencia.to_dict() for pendencia in pendencias.items],
            'total': pendencias.total,
            'pages': pendencias.pages,
            'current_page': page
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@pendencias_bp.route('/api/pendencias', methods=['POST'])
def create_pendencia():
    try:
        data = request.get_json()
        
        # Converte datas
        if data.get('data_prevista'):
            data['data_prevista'] = datetime.strptime(data['data_prevista'], '%Y-%m-%d').date()
        
        if data.get('data_finalizacao'):
            data['data_finalizacao'] = datetime.strptime(data['data_finalizacao'], '%Y-%m-%d').date()
        
        pendencia = Pendencia(**data)
        db.session.add(pendencia)
        db.session.commit()
        
        return jsonify(pendencia.to_dict()), 201
    except IntegrityError:
        db.session.rollback()
        return jsonify({'error': 'Erro de integridade dos dados'}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@pendencias_bp.route('/api/pendencias/<int:pendencia_id>', methods=['GET'])
def get_pendencia(pendencia_id):
    try:
        pendencia = Pendencia.query.get_or_404(pendencia_id)
        return jsonify(pendencia.to_dict())
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@pendencias_bp.route('/api/pendencias/<int:pendencia_id>', methods=['PUT'])
def update_pendencia(pendencia_id):
    try:
        pendencia = Pendencia.query.get_or_404(pendencia_id)
        data = request.get_json()
        
        # Converte datas
        if data.get('data_prevista'):
            data['data_prevista'] = datetime.strptime(data['data_prevista'], '%Y-%m-%d').date()
        
        if data.get('data_finalizacao'):
            data['data_finalizacao'] = datetime.strptime(data['data_finalizacao'], '%Y-%m-%d').date()
        
        # Atualiza campos
        for key, value in data.items():
            if hasattr(pendencia, key):
                setattr(pendencia, key, value)
        
        pendencia.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify(pendencia.to_dict())
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@pendencias_bp.route('/api/pendencias/<int:pendencia_id>/arquivar', methods=['PUT'])
def arquivar_pendencia(pendencia_id):
    try:
        pendencia = Pendencia.query.get_or_404(pendencia_id)
        pendencia.arquivado = True
        pendencia.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({'message': 'Pendência arquivada com sucesso'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@pendencias_bp.route('/api/pendencias/<int:pendencia_id>/desarquivar', methods=['PUT'])
def desarquivar_pendencia(pendencia_id):
    try:
        pendencia = Pendencia.query.get_or_404(pendencia_id)
        pendencia.arquivado = False
        pendencia.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({'message': 'Pendência desarquivada com sucesso'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500
