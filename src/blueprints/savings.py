"""Controlador para metas de ahorro."""

import flask
from flask_login import login_required, current_user
from model.savingsgoaldto import SavingsGoalDto
from sirope.oid import OID

savings_bp = flask.Blueprint('savings', __name__, url_prefix="/savings")

ICONS_AVAILABLE = [
    {"value": "savings", "label": "Hucha"},
    {"value": "flight_takeoff", "label": "Viaje"},
    {"value": "directions_car", "label": "Coche"},
    {"value": "laptop_mac", "label": "Tecnología"},
    {"value": "home", "label": "Casa"},
    {"value": "school", "label": "Educación"},
    {"value": "favorite", "label": "Salud"},
    {"value": "redeem", "label": "Regalo"},
    {"value": "diamond", "label": "Lujo"},
    {"value": "sports_esports", "label": "Gaming"},
]

@savings_bp.route("/", methods=["GET", "POST"])
@login_required
def index():
    srp = flask.current_app.config['sirope']
    user_id = current_user.get_id()
    
    if flask.request.method == "POST":
        name = flask.request.form.get("name")
        target = flask.request.form.get("target_amount")
        icon = flask.request.form.get("icon", "savings")
        color = flask.request.form.get("color", "#ca98ff")
        
        if name and target:
            try:
                g = SavingsGoalDto(name, float(target), 0.0, icon, color, user_id)
                srp.save(g)
                flask.flash("Meta de ahorro creada correctamente.", "success")
            except Exception as e:
                flask.flash(f"Error: {e}", "error")
        else:
            flask.flash("Faltan datos obligatorios.", "error")
            
        return flask.redirect(flask.url_for("savings.index"))
    
    goals = list(srp.filter(SavingsGoalDto, lambda g: g.user_oid == user_id))
    
    # Calcular totales
    total_ahorrado = sum(g.current_amount for g in goals)
    total_objetivo = sum(g.target_amount for g in goals)
    
    return flask.render_template(
        "savings.html",
        goals=goals,
        icons=ICONS_AVAILABLE,
        total_ahorrado=total_ahorrado,
        total_objetivo=total_objetivo
    )

@savings_bp.route("/add_funds/<oid_str>", methods=["POST"])
@login_required
def add_funds(oid_str):
    srp = flask.current_app.config['sirope']
    try:
        oid = OID.from_text(oid_str)
        g = srp.load(oid)
        if g and g.user_oid == current_user.get_id():
            amount = float(flask.request.form.get("amount", 0))
            g.current_amount = g.current_amount + amount
            srp.save(g)
            flask.flash(f"Se añadieron {amount:.2f}€ a '{g.name}'.", "success")
        else:
            flask.flash("No tienes permiso.", "error")
    except Exception as e:
        flask.flash(f"Error: {e}", "error")
    return flask.redirect(flask.url_for("savings.index"))

@savings_bp.route("/delete/<oid_str>", methods=["POST"])
@login_required
def delete(oid_str):
    srp = flask.current_app.config['sirope']
    try:
        oid = OID.from_text(oid_str)
        g = srp.load(oid)
        if g and g.user_oid == current_user.get_id():
            srp.delete(oid)
            flask.flash("Meta eliminada.", "success")
        else:
            flask.flash("No tienes permiso.", "error")
    except Exception as e:
        flask.flash(f"Error: {e}", "error")
    return flask.redirect(flask.url_for("savings.index"))

@savings_bp.route("/edit/<oid_str>", methods=["POST"])
@login_required
def edit(oid_str):
    """Edición de meta de ahorro."""
    srp = flask.current_app.config['sirope']
    try:
        oid = OID.from_text(oid_str)
        g = srp.load(oid)
        if g and g.user_oid == current_user.get_id():
            name = flask.request.form.get("name")
            target = flask.request.form.get("target_amount")
            current_amt = flask.request.form.get("current_amount")
            icon = flask.request.form.get("icon")
            color = flask.request.form.get("color")
            
            if name and target:
                g.name = name
                g.target_amount = float(target)
                if current_amt is not None:
                    g.current_amount = float(current_amt)
                if icon:
                    g.icon = icon
                if color:
                    g.color = color
                srp.save(g)
                flask.flash("Meta de ahorro modificada con éxito.", "success")
        else:
            flask.flash("No tienes permiso.", "error")
    except Exception as e:
        flask.flash(f"Error al modificar: {e}", "error")
    return flask.redirect(flask.url_for("savings.index"))
