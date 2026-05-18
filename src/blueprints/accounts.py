"""Controlador para la gestión de cuentas."""

import flask
from flask_login import login_required, current_user
from model.accountdto import AccountDto
from model.transactiondto import TransactionDto
from sirope.oid import OID

accounts_bp = flask.Blueprint('accounts', __name__, url_prefix="/accounts")

@accounts_bp.route("/", methods=["GET", "POST"])
@login_required
def index():
    """Listado y creación de cuentas."""
    srp = flask.current_app.config['sirope']
    user_id = current_user.get_id()
    
    if flask.request.method == "POST":
        name = flask.request.form.get("name")
        initial_balance = flask.request.form.get("initial_balance", 0)
        
        if name:
            acc = AccountDto(name, initial_balance, user_id)
            srp.save(acc)
            flask.flash(f"Cuenta '{name}' creada con éxito.", "success")
        return flask.redirect(flask.url_for("accounts.index"))
        
    cuentas = list(srp.filter(AccountDto, lambda c: c.user_oid == user_id))
    
    # Calcular saldo real de cada cuenta (saldo inicial + transacciones)
    transacciones = list(srp.filter(TransactionDto, lambda t: t.user_oid == user_id))
    saldos = {}
    for c in cuentas:
        oid_str = str(c.__oid__)
        movimientos = sum(t.amount for t in transacciones if t.acc_oid == oid_str)
        saldos[oid_str] = c.initial_balance + movimientos
    
    return flask.render_template("accounts.html", cuentas=cuentas, saldos=saldos)

@accounts_bp.route("/delete/<oid>", methods=["POST"])
@login_required
def delete(oid):
    """Borrado de cuenta con protección de integridad (Borrado en cascada)."""
    srp = flask.current_app.config['sirope']
    
    # Integridad estructural iterando por si hay transacciones vinculadas a esta cuenta
    transacciones_asociadas = list(srp.filter(TransactionDto, lambda t: t.acc_oid == oid))
    for t in transacciones_asociadas:
        srp.delete(t.__oid__)
        
    try:
        srp.delete(OID(oid))
        flask.flash("Cuenta y todas sus transacciones asociadas eliminadas.", "success")
    except Exception as e:
        flask.flash(f"Error al eliminar: {e}", "error")
        
    return flask.redirect(flask.url_for("accounts.index"))

@accounts_bp.route("/edit/<oid>", methods=["POST"])
@login_required
def edit(oid):
    """Edición de cuenta."""
    srp = flask.current_app.config['sirope']
    try:
        acc = srp.load(OID(oid))
        if acc and acc.user_oid == current_user.get_id():
            name = flask.request.form.get("name")
            initial_balance = flask.request.form.get("initial_balance")
            if name and initial_balance is not None:
                acc.name = name
                acc.initial_balance = float(initial_balance)
                srp.save(acc)
                flask.flash(f"Cuenta '{name}' actualizada con éxito.", "success")
        else:
            flask.flash("No tienes permisos para editar esta cuenta.", "error")
    except Exception as e:
        flask.flash(f"Error al editar: {e}", "error")
    return flask.redirect(flask.url_for("accounts.index"))
