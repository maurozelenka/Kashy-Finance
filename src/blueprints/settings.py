"""Módulo de configuración del perfil del usuario."""

import os
import flask
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from model.userdto import UserDto

settings_bp = flask.Blueprint('settings', __name__)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@settings_bp.route("/settings/upload_avatar", methods=["POST"])
@login_required
def upload_avatar():
    if 'avatar' not in flask.request.files:
        return flask.jsonify({"error": "No file part"}), 400
    file = flask.request.files['avatar']
    if file.filename == '':
        return flask.jsonify({"error": "No selected file"}), 400
    if file and allowed_file(file.filename):
        filename = secure_filename(f"avatar_{current_user.get_id()}_{file.filename}")
        # Asegurar que el directorio base es src/
        upload_folder = os.path.join(flask.current_app.root_path, 'static', 'uploads', 'avatars')
        os.makedirs(upload_folder, exist_ok=True)
        file_path = os.path.join(upload_folder, filename)
        file.save(file_path)
        
        # Guardar en DB
        srp = flask.current_app.config['sirope']
        current_user.avatar_path = f"uploads/avatars/{filename}"
        srp.save(current_user)
        
        return flask.jsonify({"success": True, "avatar_path": flask.url_for('static', filename=current_user.avatar_path)})
    
    return flask.jsonify({"error": "Invalid file format"}), 400

@settings_bp.route("/settings/change_password", methods=["POST"])
@login_required
def change_password():
    data = flask.request.json
    current_pass = data.get('current_password')
    new_pass = data.get('new_password')
    
    if not current_pass or not new_pass:
        return flask.jsonify({"error": "Faltan datos"}), 400
        
    if not current_user.check_password(current_pass):
        return flask.jsonify({"error": "La contraseña actual es incorrecta"}), 400
        
    srp = flask.current_app.config['sirope']
    current_user.set_password(new_pass)
    srp.save(current_user)
    
    return flask.jsonify({"success": True})

@settings_bp.route("/settings/change_language", methods=["POST"])
@login_required
def change_language():
    data = flask.request.json
    lang = data.get('language')
    if lang in ['es', 'en']:
        srp = flask.current_app.config['sirope']
        current_user.language = lang
        srp.save(current_user)
        return flask.jsonify({"success": True, "language": lang})
    return flask.jsonify({"error": "Idioma no soportado"}), 400

@settings_bp.route("/settings/toggle_theme", methods=["POST"])
@login_required
def toggle_theme():
    srp = flask.current_app.config['sirope']
    new_theme = "light" if current_user.theme == "dark" else "dark"
    current_user.theme = new_theme
    srp.save(current_user)
    return flask.jsonify({"success": True, "theme": new_theme})

@settings_bp.route("/settings/delete_account", methods=["POST"])
@login_required
def delete_account():
    """Borrado integral del usuario y todos sus datos (Máxima integridad estructural)."""
    from model.accountdto import AccountDto
    from model.categorydto import CategoryDto
    from model.transactiondto import TransactionDto
    from model.savingsgoaldto import SavingsGoalDto
    from model.budgetdto import BudgetDto
    from flask_login import logout_user
    
    srp = flask.current_app.config['sirope']
    user_id = current_user.get_id()
    user_oid = current_user.__oid__
    
    # 1. Borrar todas sus transacciones
    for t in srp.filter(TransactionDto, lambda x: x.user_oid == user_id):
        srp.delete(t.__oid__)
        
    # 2. Borrar todas sus cuentas
    for a in srp.filter(AccountDto, lambda x: x.user_oid == user_id):
        srp.delete(a.__oid__)
        
    # 3. Borrar todas sus categorías
    for c in srp.filter(CategoryDto, lambda x: x.user_oid == user_id):
        srp.delete(c.__oid__)
        
    # 4. Borrar sus metas de ahorro
    for g in srp.filter(SavingsGoalDto, lambda x: x.user_oid == user_id):
        srp.delete(g.__oid__)
        
    # 5. Borrar sus presupuestos
    for b in srp.filter(BudgetDto, lambda x: x.user_oid == user_id):
        srp.delete(b.__oid__)
        
    # 6. Borrar el propio usuario
    srp.delete(user_oid)
    
    logout_user()
    flask.flash("Tu cuenta y todos tus datos han sido eliminados permanentemente.", "info")
    return flask.redirect(flask.url_for("auth.login"))
