"""Controlador para transacciones."""

import flask
from flask_login import login_required, current_user
from model.transactiondto import TransactionDto
from model.accountdto import AccountDto
from model.categorydto import CategoryDto
from sirope.oid import OID
import datetime

transactions_bp = flask.Blueprint('transactions', __name__, url_prefix="/transactions")

@transactions_bp.route("/", methods=["GET", "POST"])
@login_required
def index():
    srp = flask.current_app.config['sirope']
    user_id = current_user.get_id()
    
    if flask.request.method == "POST":
        amount = flask.request.form.get("amount")
        notes = flask.request.form.get("notes")
        date_str = flask.request.form.get("date_str", datetime.date.today().isoformat())
        cat_oid = flask.request.form.get("cat_oid")
        acc_oid = flask.request.form.get("acc_oid")
        
        # Validar consistencia
        if amount and cat_oid and acc_oid:
            try:
                # Comprobar que la categoría es correcta para aplicar el signo si es necesario
                cat = srp.load(OID.from_text(cat_oid))
                amount_val = float(amount)
                if cat.cat_type == 'gasto' and amount_val > 0:
                    amount_val = -amount_val # Forzamos que sea negativo
                elif cat.cat_type == 'ingreso' and amount_val < 0:
                    amount_val = abs(amount_val)
                    
                t = TransactionDto(amount_val, notes, date_str, cat_oid, acc_oid, user_id)
                srp.save(t)
                flask.flash("Transacción registrada correctamente.", "success")
            except Exception as e:
                flask.flash(f"Error procesando transacción: {e}", "error")
        else:
            flask.flash("Faltan datos obligatorios para crear la transacción.", "error")
            
        return flask.redirect(flask.url_for("transactions.index"))

    # Para renderizar el form:
    cuentas = list(srp.filter(AccountDto, lambda a: a.user_oid == user_id))
    categorias = list(srp.filter(CategoryDto, lambda c: c.user_oid == user_id))
    
    transacciones = list(srp.filter(TransactionDto, lambda t: t.user_oid == user_id))
    transacciones.sort(key=lambda x: x.date_str, reverse=True)
    
    # Mapeos para que en Jinja2 podamos mostrar nombres en lugar de OIDs
    cat_map = {str(c.__oid__): c for c in categorias}
    acc_map = {str(a.__oid__): a.name for a in cuentas}
    
    # Saldo real por cuenta para mostrar en el selector
    saldos = {}
    for c in cuentas:
        oid_str = str(c.__oid__)
        movimientos = sum(t.amount for t in transacciones if t.acc_oid == oid_str)
        saldos[oid_str] = c.initial_balance + movimientos
    
    return flask.render_template(
        "transactions.html", 
        transacciones=transacciones, 
        cuentas=cuentas, 
        categorias=categorias,
        cat_map=cat_map,
        acc_map=acc_map,
        saldos=saldos,
        today=datetime.date.today().isoformat()
    )

@transactions_bp.route("/delete/<oid_str>", methods=["POST"])
@login_required
def delete(oid_str):
    srp = flask.current_app.config['sirope']
    try:
        oid = OID.from_text(oid_str)
        t = srp.load(oid)
        
        # Verificar que la transacción pertenece al usuario actual
        if t and t.user_oid == current_user.get_id():
            srp.delete(oid)
            flask.flash("Transacción eliminada.", "success")
        else:
            flask.flash("No tienes permiso para eliminar esta transacción.", "error")
            
    except Exception as e:
        flask.flash(f"Error al eliminar la transacción: {e}", "error")
        
    return flask.redirect(flask.url_for("transactions.index"))

@transactions_bp.route("/edit/<oid_str>", methods=["POST"])
@login_required
def edit(oid_str):
    """Edición de transacción."""
    srp = flask.current_app.config['sirope']
    try:
        oid = OID.from_text(oid_str)
        t = srp.load(oid)
        if t and t.user_oid == current_user.get_id():
            amount = flask.request.form.get("amount")
            notes = flask.request.form.get("notes")
            date_str = flask.request.form.get("date_str")
            cat_oid = flask.request.form.get("cat_oid")
            acc_oid = flask.request.form.get("acc_oid")
            
            if amount and cat_oid and acc_oid:
                cat = srp.load(OID.from_text(cat_oid))
                amount_val = float(amount)
                if cat.cat_type == 'gasto' and amount_val > 0:
                    amount_val = -amount_val
                elif cat.cat_type == 'ingreso' and amount_val < 0:
                    amount_val = abs(amount_val)
                    
                t.amount = amount_val
                t.notes = notes
                t.date_str = date_str
                t.cat_oid = cat_oid
                t.acc_oid = acc_oid
                srp.save(t)
                flask.flash("Transacción modificada con éxito.", "success")
        else:
            flask.flash("No tienes permisos para editar esta transacción.", "error")
    except Exception as e:
        flask.flash(f"Error al modificar: {e}", "error")
    return flask.redirect(flask.url_for("transactions.index"))
