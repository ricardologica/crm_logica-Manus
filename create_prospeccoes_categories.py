#!/usr/bin/env python3

import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from src.models.user import db
from src.models.configuracoes import Categoria, Subcategoria
from src.main import app

def create_sample_categories():
    """Cria categorias de exemplo para o módulo de Prospecções"""
    
    categories_data = [
        {
            'name': 'Status Prospecção',
            'tipo': 'status_prospeccao',
            'subcategorias': [
                'Em andamento',
                'Aguardando retorno',
                'Proposta enviada',
                'Negociação',
                'Fechado - Ganho',
                'Fechado - Perdido',
                'Cancelado'
            ]
        },
        {
            'name': 'Natureza do Contrato',
            'tipo': 'natureza_contrato',
            'subcategorias': [
                'Telefonia Fixa',
                'Telefonia Móvel',
                'Internet',
                'Dados',
                'Voz sobre IP (VoIP)',
                'Serviços de Rede'
            ]
        },
        {
            'name': 'Follow-up',
            'tipo': 'followup',
            'subcategorias': [
                'Ligar em 1 dia',
                'Ligar em 3 dias',
                'Ligar em 1 semana',
                'Ligar em 15 dias',
                'Ligar em 1 mês',
                'Enviar e-mail',
                'Enviar WhatsApp'
            ]
        },
        {
            'name': 'Consultor',
            'tipo': 'consultor',
            'subcategorias': [
                'João Silva',
                'Maria Santos',
                'Pedro Oliveira',
                'Ana Costa'
            ]
        },
        {
            'name': 'Tipo de Aceite de Contrato',
            'tipo': 'tipo_aceite_contrato',
            'subcategorias': [
                'Assinatura física',
                'Assinatura digital',
                'E-mail de confirmação',
                'WhatsApp',
                'Verbal (gravado)'
            ]
        }
    ]
    
    with app.app_context():
        for cat_data in categories_data:
            # Verifica se a categoria já existe
            existing_category = Categoria.query.filter_by(
                nome=cat_data['name'], 
                tipo=cat_data['tipo']
            ).first()
            
            if not existing_category:
                # Cria a categoria
                categoria = Categoria(
                    nome=cat_data['name'],
                    tipo=cat_data['tipo'],
                    descricao=f"Categoria para {cat_data['name']}"
                )
                db.session.add(categoria)
                db.session.flush()  # Para obter o ID da categoria
                
                # Cria as subcategorias
                for sub_name in cat_data['subcategorias']:
                    subcategoria = Subcategoria(
                        nome=sub_name,
                        categoria_id=categoria.id
                    )
                    db.session.add(subcategoria)
                
                print(f"Categoria '{cat_data['name']}' criada com {len(cat_data['subcategorias'])} subcategorias")
            else:
                print(f"Categoria '{cat_data['name']}' já existe")
        
        db.session.commit()
        print("Categorias de exemplo criadas com sucesso!")

if __name__ == '__main__':
    create_sample_categories()

