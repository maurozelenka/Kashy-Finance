"""Controlador para la gestión de categorías."""

import flask
from flask_login import login_required, current_user
from model.categorydto import CategoryDto
from sirope.oid import OID

categories_bp = flask.Blueprint('categories', __name__, url_prefix="/categories")

@categories_bp.route("/", methods=["GET", "POST"])
@login_required
def index():
    """Listado y creación de categorías."""
    srp = flask.current_app.config['sirope']
    user_id = current_user.get_id()
    
    if flask.request.method == "POST":
        name = flask.request.form.get("name")
        cat_type = flask.request.form.get("type")
        color = flask.request.form.get("color", "#8a2be2")
        icon = flask.request.form.get("icon", "category")
        
        if name and cat_type:
            cat = CategoryDto(name, cat_type, color, user_id, icon)
            srp.save(cat)
            flask.flash(f"Categoría '{name}' creada.", "success")
        else:
            flask.flash("Faltan datos obligatorios.", "error")
            
        return flask.redirect(flask.url_for("categories.index"))
        
    categorias = list(srp.filter(CategoryDto, lambda c: c.user_oid == user_id))
    return flask.render_template("categories.html", categorias=categorias)

from model.transactiondto import TransactionDto

@categories_bp.route("/delete/<oid>", methods=["POST"])
@login_required
def delete(oid):
    """Borrado de categoría con integridad estructural (Borrado en cascada)."""
    srp = flask.current_app.config['sirope']
    
    # Borrado en cascada: Eliminar transacciones que usan esta categoría
    transacciones_asociadas = list(srp.filter(TransactionDto, lambda t: t.cat_oid == oid))
    for t in transacciones_asociadas:
        srp.delete(t.__oid__)
        
    try:
        srp.delete(OID(oid))
        flask.flash("Categoría y sus transacciones asociadas eliminadas con éxito.", "success")
    except Exception as e:
        flask.flash("Error al eliminar categoría.", "error")
        
    return flask.redirect(flask.url_for("categories.index"))
