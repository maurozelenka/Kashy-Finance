import os
import sys
import flask
from flask_login import LoginManager
import sirope
from sirope.oid import OID

# Asegurar que el directorio src está en el path de Python (Fix para Render/Linux)
basedir = os.path.abspath(os.path.dirname(__file__))
if basedir not in sys.path:
    sys.path.insert(0, basedir)

def create_app():
    """Factory de creación de la aplicación web."""
    app = flask.Flask(__name__)
    app.secret_key = 'als_secret_key_fixed'
    
    # Inicialización de sirope con fallback a fakeredis para Render
    import redis
    import fakeredis
    import sirope.safeindex

    redis_url = os.environ.get('REDIS_URL')
    if redis_url:
        try:
            r = redis.from_url(redis_url)
            r.ping()
            srp = sirope.Sirope(redis_obj=r)
        except Exception:
            print("⚠️ Error con REDIS_URL. Usando fakeredis...")
            sirope.safeindex.SafeIndex.instance = None
            srp = sirope.Sirope(redis_obj=fakeredis.FakeRedis())
    else:
        print("ℹ️ REDIS_URL no encontrada. Usando fakeredis...")
        sirope.safeindex.SafeIndex.instance = None
        srp = sirope.Sirope(redis_obj=fakeredis.FakeRedis())
    
    # Auto-seed del usuario demo para pruebas y TFG
    try:
        from utils.seeder import seed_demo_data
        seed_demo_data(srp)
    except Exception as e:
        print(f"❌ Error en el auto-seed: {e}")
    
    app.config['sirope'] = srp
    
    # Flask-Login
    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.login_message = "Por favor, inicia sesión para acceder."
    login_manager.init_app(app)
    
    @login_manager.user_loader
    def load_user(user_id):
        print(f"DEBUG: Cargando usuario con ID: {user_id}")
        if not user_id or user_id == "None":
            return None
        try:
            # user_id viene como "model.userdto.UserDto@13"
            # Usamos OID.from_text() para reconstruir el OID desde el string
            oid = OID.from_text(user_id)
            u = srp.load(oid)
            print(f"DEBUG: Usuario cargado correctamente: {u.email if (u and hasattr(u, 'email')) else 'None'}")
            return u
        except Exception as e:
            print(f"DEBUG: ERROR cargando usuario: {e}")
            return None
            
    # Registro de blueprints en un bloque try para que no falle si no se han creado
    try:
        from blueprints.auth import auth_bp
        from blueprints.dashboard import dashboard_bp
        from blueprints.accounts import accounts_bp
        from blueprints.categories import categories_bp
        from blueprints.transactions import transactions_bp
        from blueprints.budgets import budgets_bp
        from blueprints.savings import savings_bp
        from blueprints.settings import settings_bp
        
        app.register_blueprint(auth_bp)
        app.register_blueprint(dashboard_bp)
        app.register_blueprint(accounts_bp)
        app.register_blueprint(categories_bp)
        app.register_blueprint(transactions_bp)
        app.register_blueprint(budgets_bp)
        app.register_blueprint(savings_bp)
        app.register_blueprint(settings_bp)
    except ImportError as e:
        print(f"Buscando dependencias o blueprints no implementados aún: {e}")
    
    @app.route("/")
    def index():
        from flask_login import current_user
        if current_user.is_authenticated:
            return flask.redirect(flask.url_for("dashboard.index" if "dashboard.index" in [e.endpoint for e in app.url_map.iter_rules()] else "auth.login"))
        return flask.render_template("landing.html")
        
    return app

# Facilita el comando > flask run
app = create_app()

if __name__ == "__main__":
    app.run(debug=True)
