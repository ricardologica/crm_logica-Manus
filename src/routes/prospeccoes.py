from flask import Blueprint, request, jsonify
from src.models.user import db
from src.models.prospeccoes import Prospeccao
from src.models.configuracoes import Categoria
from sqlalchemy.exc import IntegrityError
from datetime import datetime
import re

prospeccoes_bp = Blueprint('prospeccoes', __name__)

def validate_cpf(cpf):
    """Valida CPF"""
    cpf = re.sub(r'[^0-9]', '', cpf)
    if len(cpf) != 11:
        return False
    
    # Verifica se todos os dígitos são iguais
    if cpf == cpf[0] * 11:
        return False
    
    # Calcula o primeiro dígito verificador
    sum1 = sum(int(cpf[i]) * (10 - i) for i in range(9))
    digit1 = 11 - (sum1 % 11)
    if digit1 >= 10:
        digit1 = 0
    
    # Calcula o segundo dígito verificador
    sum2 = sum(int(cpf[i]) * (11 - i) for i in range(10))
    digit2 = 11 - (sum2 % 11)
    if digit2 >= 10:
        digit2 = 0
    
    return cpf[-2:] == f"{digit1}{digit2}"

def validate_cnpj(cnpj):
    """Valida CNPJ"""
    cnpj = re.sub(r'[^0-9]', '', cnpj)
    if len(cnpj) != 14:
        return False
    
    # Verifica se todos os dígitos são iguais
    if cnpj == cnpj[0] * 14:
        return False
    
    # Calcula o primeiro dígito verificador
    weights1 = [5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
    sum1 = sum(int(cnpj[i]) * weights1[i] for i in range(12))
    digit1 = 11 - (sum1 % 11)
    if digit1 >= 10:
        digit1 = 0
    
    # Calcula o segundo dígito verificador
    weights2 = [6, 5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
    sum2 = sum(int(cnpj[i]) * weights2[i] for i in range(13))
    digit2 = 11 - (sum2 % 11)
    if digit2 >= 10:
        digit2 = 0
    
    return cnpj[-2:] == f"{digit1}{digit2}"

def validate_email(email):
    """Valida e-mail"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def validate_celular(celular):
    """Valida celular"""
    pattern = r'^\(\d{2}\)\s\d{4,5}-\d{4}$'
    return re.match(pattern, celular) is not None

@prospeccoes_bp.route('/api/prospeccoes', methods=['GET'])
def get_prospeccoes():
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        search = request.args.get('search', '')
        arquivado = request.args.get('arquivado', 'false').lower() == 'true'
        
        query = Prospeccao.query.filter_by(arquivado=arquivado)
        
        if search:
            query = query.filter(
                db.or_(
                    Prospeccao.numero_contrato.contains(search),
                    Prospeccao.nome_razao_social.contains(search),
                    Prospeccao.nome_responsavel.contains(search),
                    Prospeccao.cpf_cnpj.contains(search)
                )
            )
        
        prospeccoes = query.order_by(Prospeccao.created_at.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        return jsonify({
            'prospeccoes': [prospeccao.to_dict() for prospeccao in prospeccoes.items],
            'total': prospeccoes.total,
            'pages': prospeccoes.pages,
            'current_page': page
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@prospeccoes_bp.route('/api/prospeccoes', methods=['POST'])
def create_prospeccao():
    try:
        data = request.get_json()
        
        # Validações
        if data.get('tipo_pessoa') == 'PF':
            if not validate_cpf(data.get('cpf_cnpj', '')):
                return jsonify({'error': 'CPF inválido'}), 400
        elif data.get('tipo_pessoa') == 'PJ':
            if not validate_cnpj(data.get('cpf_cnpj', '')):
                return jsonify({'error': 'CNPJ inválido'}), 400
        
        if not validate_email(data.get('email', '')):
            return jsonify({'error': 'E-mail inválido'}), 400
        
        if not validate_celular(data.get('celular', '')):
            return jsonify({'error': 'Celular inválido. Use o formato (XX) XXXXX-XXXX'}), 400
        
        # Converte datas
        if data.get('data_entrada'):
            data['data_entrada'] = datetime.strptime(data['data_entrada'], '%Y-%m-%d').date()
        
        if data.get('data_aceite'):
            data['data_aceite'] = datetime.strptime(data['data_aceite'], '%Y-%m-%d').date()
        
        prospeccao = Prospeccao(**data)
        
        # Define natureza do contrato se fornecida
        if data.get('natureza_contrato_ids'):
            prospeccao.set_natureza_contrato_ids(data['natureza_contrato_ids'])
        
        db.session.add(prospeccao)
        db.session.commit()
        
        return jsonify(prospeccao.to_dict()), 201
    except IntegrityError:
        db.session.rollback()
        return jsonify({'error': 'Erro de integridade dos dados'}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@prospeccoes_bp.route('/api/prospeccoes/<int:prospeccao_id>', methods=['GET'])
def get_prospeccao(prospeccao_id):
    try:
        prospeccao = Prospeccao.query.get_or_404(prospeccao_id)
        return jsonify(prospeccao.to_dict())
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@prospeccoes_bp.route('/api/prospeccoes/<int:prospeccao_id>', methods=['PUT'])
def update_prospeccao(prospeccao_id):
    try:
        prospeccao = Prospeccao.query.get_or_404(prospeccao_id)
        data = request.get_json()
        
        # Validações
        if data.get('tipo_pessoa') == 'PF':
            if not validate_cpf(data.get('cpf_cnpj', '')):
                return jsonify({'error': 'CPF inválido'}), 400
        elif data.get('tipo_pessoa') == 'PJ':
            if not validate_cnpj(data.get('cpf_cnpj', '')):
                return jsonify({'error': 'CNPJ inválido'}), 400
        
        if data.get('email') and not validate_email(data['email']):
            return jsonify({'error': 'E-mail inválido'}), 400
        
        if data.get('celular') and not validate_celular(data['celular']):
            return jsonify({'error': 'Celular inválido. Use o formato (XX) XXXXX-XXXX'}), 400
        
        # Converte datas
        if data.get('data_entrada'):
            data['data_entrada'] = datetime.strptime(data['data_entrada'], '%Y-%m-%d').date()
        
        if data.get('data_aceite'):
            data['data_aceite'] = datetime.strptime(data['data_aceite'], '%Y-%m-%d').date()
        
        # Atualiza campos
        for key, value in data.items():
            if key != 'natureza_contrato_ids' and hasattr(prospeccao, key):
                setattr(prospeccao, key, value)
        
        # Atualiza natureza do contrato se fornecida
        if 'natureza_contrato_ids' in data:
            prospeccao.set_natureza_contrato_ids(data['natureza_contrato_ids'])
        
        prospeccao.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify(prospeccao.to_dict())
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@prospeccoes_bp.route('/api/prospeccoes/<int:prospeccao_id>/arquivar', methods=['PUT'])
def arquivar_prospeccao(prospeccao_id):
    try:
        prospeccao = Prospeccao.query.get_or_404(prospeccao_id)
        prospeccao.arquivado = True
        prospeccao.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({'message': 'Prospecção arquivada com sucesso'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@prospeccoes_bp.route('/api/prospeccoes/<int:prospeccao_id>/desarquivar', methods=['PUT'])
def desarquivar_prospeccao(prospeccao_id):
    try:
        prospeccao = Prospeccao.query.get_or_404(prospeccao_id)
        prospeccao.arquivado = False
        prospeccao.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({'message': 'Prospecção desarquivada com sucesso'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@prospeccoes_bp.route('/api/prospeccoes/<int:prospeccao_id>', methods=['DELETE'])
def delete_prospeccao(prospeccao_id):
    try:
        prospeccao = Prospeccao.query.get_or_404(prospeccao_id)
        db.session.delete(prospeccao)
        db.session.commit()
        
        return jsonify({'message': 'Prospecção excluída com sucesso'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

