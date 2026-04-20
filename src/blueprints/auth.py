"""Módulo de autenticación (Login, Registro)."""

import flask
from flask_login import login_user, logout_user, login_required
from model.userdto import UserDto
from model.categorydto import CategoryDto

auth_bp = flask.Blueprint('auth', __name__)

# Categorías que se crean automáticamente para cada usuario nuevo
_DEFAULT_CATEGORIES = [
    ("Alimentación", "gasto",  "#ff6e40"),
    ("Transporte",   "gasto",  "#448aff"),
    ("Ocio",         "gasto",  "#b388ff"),
    ("Hogar",        "gasto",  "#ff5252"),
    ("Nómina",       "ingreso","#69f0ae"),
    ("Otros Ingresos","ingreso","#40c4ff"),
]

@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    """Ruta para inicio de sesión."""
    if flask.request.method == "POST":
        email = flask.request.form.get("email")
        password = flask.request.form.get("password")
        
        srp = flask.current_app.config['sirope']
        user = UserDto.current_user(srp, email)
        
        if user and user.check_password(password):
            login_user(user)
            flask.flash("Inicio de sesión exitoso.", "success")
            return flask.redirect(flask.url_for("dashboard.index"))
        
        flask.flash("Credenciales incorrectas.", "error")
            
    return flask.render_template("login.html")

@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    """Ruta para registro de usuarios nuevos."""
    if flask.request.method == "POST":
        email = flask.request.form.get("email")
        password = flask.request.form.get("password")
        
        srp = flask.current_app.config['sirope']
        
        existing = UserDto.current_user(srp, email)
        if existing:
            flask.flash("El usuario ya existe.", "error")
            return flask.redirect(flask.url_for("auth.register"))
            
        new_user = UserDto(email, password)
        srp.save(new_user)
        
        # Crear categorías por defecto para el nuevo usuario
        user_id = new_user.get_id()
        for name, cat_type, color in _DEFAULT_CATEGORIES:
            srp.save(CategoryDto(name, cat_type, color, user_id))
        
        flask.flash("¡Cuenta creada! Ya tienes categorías listas para empezar.", "success")
        return flask.redirect(flask.url_for("auth.login"))

    return flask.render_template("register.html")

@auth_bp.route("/logout")
@login_required
def logout():
    """Ruta para cerrar sesión."""
    logout_user()
    flask.flash("Sesión cerrada.", "info")
    return flask.redirect(flask.url_for("auth.login"))
 
