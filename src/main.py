import os
import sys
# DON'T CHANGE THIS !!!
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from flask import Flask, send_from_directory
from flask_cors import CORS
from src.models.user import db
from src.models.configuracoes import Categoria, Subcategoria
from src.models.prospeccoes import Prospeccao
from src.models.pendencias import Pendencia # Nova importação
from src.models.filiais import Filial # Nova importação
from src.routes.user import user_bp
from src.routes.configuracoes import configuracoes_bp
from src.routes.prospeccoes import prospeccoes_bp
from src.routes.pendencias import pendencias_bp # Nova importação
from src.routes.filiais import filiais_bp # Nova importação

app = Flask(__name__, static_folder=os.path.join(os.path.dirname(__file__), 'static'))
app.config['SECRET_KEY'] = 'asdf#FGSgvasgf$5$WGT'

# Habilitar CORS para permitir requisições do frontend
CORS(app)

app.register_blueprint(user_bp, url_prefix='/api')
app.register_blueprint(configuracoes_bp, url_prefix='/api')
app.register_blueprint(prospeccoes_bp) # Já existia
app.register_blueprint(pendencias_bp) # Novo registro
app.register_blueprint(filiais_bp) # Novo registro

# uncomment if you need to use database
app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql://crmlogicadb_owner:npg_toClPehVNJ97@ep-wandering-bread-a8al5awo-pooler.eastus2.azure.neon.tech/crmlogicadb?sslmode=require"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)
with app.app_context():
    db.create_all()

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve(path):
    static_folder_path = app.static_folder
    if static_folder_path is None:
            return "Static folder not configured", 404

    if path != "" and os.path.exists(os.path.join(static_folder_path, path)):
        return send_from_directory(static_folder_path, path)
    else:
        index_path = os.path.join(static_folder_path, 'index.html')
        if os.path.exists(index_path):
            return send_from_directory(static_folder_path, 'index.html')
        else:
            return "index.html not found", 404


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5001))
    app.run(host='0.0.0.0', port=port, debug=True)
