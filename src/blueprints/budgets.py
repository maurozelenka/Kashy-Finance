"""Controlador para presupuestos mensuales."""

import flask
from flask_login import login_required, current_user
from model.budgetdto import BudgetDto
from model.categorydto import CategoryDto
from model.transactiondto import TransactionDto
from sirope.oid import OID
import datetime

budgets_bp = flask.Blueprint('budgets', __name__, url_prefix="/budgets")

@budgets_bp.route("/", methods=["GET", "POST"])
@login_required
def index():
    srp = flask.current_app.config['sirope']
    user_id = current_user.get_id()
    
    if flask.request.method == "POST":
        cat_oid = flask.request.form.get("cat_oid")
        limit_amount = flask.request.form.get("limit_amount")
        
        if cat_oid and limit_amount:
            try:
                # Comprobar si ya existe un presupuesto para esta categoría
                existing = list(srp.filter(BudgetDto, lambda b: b.user_oid == user_id and b.cat_oid == cat_oid))
                if existing:
                    # Actualizar el existente
                    existing[0].limit_amount = float(limit_amount)
                    srp.save(existing[0])
                    flask.flash("Presupuesto actualizado correctamente.", "success")
                else:
                    b = BudgetDto(cat_oid, float(limit_amount), user_id)
                    srp.save(b)
                    flask.flash("Presupuesto creado correctamente.", "success")
            except Exception as e:
                flask.flash(f"Error: {e}", "error")
        else:
            flask.flash("Faltan datos obligatorios.", "error")
            
        return flask.redirect(flask.url_for("budgets.index"))
    
    # Cargar categorías de gasto y presupuestos
    categorias = list(srp.filter(CategoryDto, lambda c: c.user_oid == user_id and c.cat_type == 'gasto'))
    budgets = list(srp.filter(BudgetDto, lambda b: b.user_oid == user_id))
    transacciones = list(srp.filter(TransactionDto, lambda t: t.user_oid == user_id))
    
    # Calcular gasto actual del mes para cada presupuesto
    hoy = datetime.date.today()
    month_start = hoy.replace(day=1).isoformat()
    if hoy.month == 12:
        month_end = hoy.replace(year=hoy.year + 1, month=1, day=1).isoformat()
    else:
        month_end = hoy.replace(month=hoy.month + 1, day=1).isoformat()
    
    cat_map = {str(c.__oid__): c for c in categorias}
    
    budget_data = []
    for b in budgets:
        cat = cat_map.get(b.cat_oid)
        if not cat:
            continue
        
        # Gastos de este mes en esta categoría
        gastado = sum(abs(t.amount) for t in transacciones 
                      if t.cat_oid == b.cat_oid and t.amount < 0 
                      and month_start <= t.date_str < month_end)
        
        porcentaje = min((gastado / b.limit_amount * 100), 100) if b.limit_amount > 0 else 0
        
        budget_data.append({
            "oid": str(b.__oid__),
            "cat_name": cat.name,
            "cat_color": cat.color,
            "limit": b.limit_amount,
            "spent": gastado,
            "remaining": max(b.limit_amount - gastado, 0),
            "pct": porcentaje,
            "over": gastado > b.limit_amount
        })
    
    # Categorías que NO tienen presupuesto aún
    cats_con_budget = {b.cat_oid for b in budgets}
    cats_sin_budget = [c for c in categorias if str(c.__oid__) not in cats_con_budget]
    
    return flask.render_template(
        "budgets.html",
        budget_data=budget_data,
        cats_sin_budget=cats_sin_budget,
        mes_label=hoy.strftime("%B %Y")
    )

@budgets_bp.route("/delete/<oid_str>", methods=["POST"])
@login_required
def delete(oid_str):
    srp = flask.current_app.config['sirope']
    try:
        oid = OID.from_text(oid_str)
        b = srp.load(oid)
        if b and b.user_oid == current_user.get_id():
            srp.delete(oid)
            flask.flash("Presupuesto eliminado.", "success")
        else:
            flask.flash("No tienes permiso.", "error")
    except Exception as e:
        flask.flash(f"Error: {e}", "error")
    return flask.redirect(flask.url_for("budgets.index"))
