"""Controlador del Dashboard Principal."""

import flask
from flask_login import login_required, current_user
from model.accountdto import AccountDto
from model.transactiondto import TransactionDto
from model.categorydto import CategoryDto
from sirope.oid import OID
import datetime
import json

dashboard_bp = flask.Blueprint('dashboard', __name__, url_prefix="/dashboard")

@dashboard_bp.route("/")
@login_required
def index():
    """Muestra el resumen financiero del usuario (Saldo y últimas transacciones)."""
    srp = flask.current_app.config['sirope']
    user_id = current_user.get_id()
    
    # Obtener mes y año de la URL o usar los actuales
    hoy = datetime.date.today()
    try:
        req_month = int(flask.request.args.get('month', hoy.month))
        req_year = int(flask.request.args.get('year', hoy.year))
        # Validar fecha
        view_date = datetime.date(req_year, req_month, 1)
    except (ValueError, TypeError):
        req_month, req_year = hoy.month, hoy.year
        view_date = hoy.replace(day=1)

    # Cargar datos del usuario
    cuentas = list(srp.filter(AccountDto, lambda a: a.user_oid == user_id))
    transacciones = list(srp.filter(TransactionDto, lambda t: t.user_oid == user_id))
    
    # Ordenar transacciones por fecha descendente
    transacciones.sort(key=lambda x: x.date_str, reverse=True)
    
    saldo_total = sum(c.initial_balance for c in cuentas) + sum(t.amount for t in transacciones)
    
    # Calcular ingresos y gastos del mes seleccionado
    month_start = view_date.replace(day=1).isoformat()
    if req_month == 12:
        month_end = view_date.replace(year=req_year + 1, month=1, day=1).isoformat()
    else:
        month_end = view_date.replace(month=req_month + 1, day=1).isoformat()
        
    income_mensual = sum(t.amount for t in transacciones if t.amount > 0 and month_start <= t.date_str < month_end)
    expense_mensual = sum(abs(t.amount) for t in transacciones if t.amount < 0 and month_start <= t.date_str < month_end)

    # Precalcular balance neto por día (todas las transacciones)
    balance_diario = {}
    for t in transacciones:
        balance_diario[t.date_str] = balance_diario.get(t.date_str, 0) + t.amount

    # === VISTA SEMANA: Barras de los últimos 7 días (siempre respecto a hoy) ===
    days_en = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
    days_es = ["Lun", "Mar", "Mié", "Jue", "Vie", "Sáb", "Dom"]
    
    chart_week = []
    for i in range(6, -1, -1):
        dia = hoy - datetime.timedelta(days=i)
        dia_str = dia.isoformat()
        net = balance_diario.get(dia_str, 0)
        
        # Localizar día
        if current_user.language == 'en':
            label = days_en[dia.weekday()]
        else:
            label = days_es[dia.weekday()]
            
        chart_week.append({
            "label": label,
            "net": net,
            "abs": abs(net),
        })
    week_max = max((d["abs"] for d in chart_week), default=1) or 1

    # === CÁLCULO DINÁMICO DE TARJETAS DE RESUMEN SEMANAL ===
    semana_start = (hoy - datetime.timedelta(days=6)).isoformat()
    semana_end = (hoy + datetime.timedelta(days=1)).isoformat()
    
    income_semana = sum(t.amount for t in transacciones if t.amount > 0 and semana_start <= t.date_str < semana_end)
    expense_semana = sum(abs(t.amount) for t in transacciones if t.amount < 0 and semana_start <= t.date_str < semana_end)
    savings_semana = income_semana - expense_semana

    prev_semana_start = (hoy - datetime.timedelta(days=13)).isoformat()
    prev_semana_end = (hoy - datetime.timedelta(days=6)).isoformat()
    
    prev_income_semana = sum(t.amount for t in transacciones if t.amount > 0 and prev_semana_start <= t.date_str < prev_semana_end)
    prev_expense_semana = sum(abs(t.amount) for t in transacciones if t.amount < 0 and prev_semana_start <= t.date_str < prev_semana_end)
    prev_savings_semana = prev_income_semana - prev_expense_semana

    def calc_pct_change(curr, prev):
        if prev != 0:
            return ((curr - prev) / abs(prev)) * 100
        return 100.0 if curr > 0 else (-100.0 if curr < 0 else 0.0)

    income_change_pct = calc_pct_change(income_semana, prev_income_semana)
    expense_change_pct = calc_pct_change(expense_semana, prev_expense_semana)
    savings_change_pct = calc_pct_change(savings_semana, prev_savings_semana)

    # === VISTA MES: Cuadrícula del mes seleccionado ===
    primer_dia_mes = view_date.replace(day=1)
    if req_month == 12:
        ultimo_dia_mes = datetime.date(req_year, 12, 31)
    else:
        ultimo_dia_mes = (view_date.replace(month=req_month + 1, day=1) - datetime.timedelta(days=1))
    
    chart_month = []
    dia_cursor = primer_dia_mes
    while dia_cursor <= ultimo_dia_mes:
        dia_str = dia_cursor.isoformat()
        net = balance_diario.get(dia_str, 0)
        es_futuro = dia_cursor > hoy
        chart_month.append({
            "day": dia_cursor.day,
            "net": net,
            "future": es_futuro,
            "weekday": dia_cursor.weekday(),
        })
        dia_cursor += datetime.timedelta(days=1)
    
    pad_inicio = primer_dia_mes.weekday()

    # === VISTA AÑO: 12 meses del año seleccionado ===
    chart_year = []
    for m in range(1, 13):
        p_dia = datetime.date(req_year, m, 1)
        if m == 12:
            u_dia = datetime.date(req_year, 12, 31)
        else:
            u_dia = datetime.date(req_year, m + 1, 1) - datetime.timedelta(days=1)
        
        net_mes = 0
        d_cursor = p_dia
        while d_cursor <= u_dia:
            net_mes += balance_diario.get(d_cursor.isoformat(), 0)
            d_cursor += datetime.timedelta(days=1)
        
        months_en = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
        months_es = ["Ene", "Feb", "Mar", "Abr", "May", "Jun", "Jul", "Ago", "Sep", "Oct", "Nov", "Dic"]
        
        if current_user.language == 'en':
            m_label = months_en[m-1]
        else:
            m_label = months_es[m-1]
            
        chart_year.append({
            "label": m_label,
            "net": net_mes,
            "abs": abs(net_mes),
            "future": p_dia > hoy,
        })
    year_max = max((d["abs"] for d in chart_year), default=1) or 1

    # === VISTA PATRIMONIO: Estilo Infografía (2020-2030) ===
    total_inicial = sum(c.initial_balance for c in cuentas)
    chart_patrimonio = []
    meta_objetivo = 1000000 # Meta de ejemplo (1M €)
    
    for año in range(2020, 2031):
        fecha_limite = f"{año}-12-31"
        # Comprobar si hay transacciones específicamente en ESTE año
        trans_este_año = [t for t in transacciones if t.date_str.startswith(str(año))]
        tiene_actividad = len(trans_este_año) > 0
        
        # El patrimonio acumulado sigue siendo la suma de todo hasta ese momento
        neto_hasta_entonces = sum(t.amount for t in transacciones if t.date_str <= fecha_limite)
        acumulado = total_inicial + neto_hasta_entonces
        
        chart_patrimonio.append({
            "label": str(año),
            "net": acumulado if tiene_actividad else 0,
            "abs": abs(acumulado) if tiene_actividad else 0,
            "es_futuro": not tiene_actividad # Usamos la misma clase visual para años sin actividad
        })
    
    wealth_max = max((d["abs"] for d in chart_patrimonio), default=1) or 1
    
    # Datos para las tarjetas de activos (agrupamos por nombre de cuenta)
    resumen_cuentas = []
    for c in cuentas:
        oid_str = str(c.__oid__)
        movs = sum(t.amount for t in transacciones if t.acc_oid == oid_str)
        resumen_cuentas.append({
            "name": c.name,
            "balance": c.initial_balance + movs
        })

    # Navegación
    prev_month = (view_date - datetime.timedelta(days=1)).month
    prev_year_m = (view_date - datetime.timedelta(days=1)).year
    next_month = (ultimo_dia_mes + datetime.timedelta(days=1)).month
    next_year_m = (ultimo_dia_mes + datetime.timedelta(days=1)).year
    
    # === VISTA HERO CHART (Smooth Area Chart con Selector de Periodo) ===
    hero_period = flask.request.args.get('hero_period', '30D')
    if hero_period == '1D':
        dias_totales = 1
    elif hero_period == '7D':
        dias_totales = 7
    elif hero_period == '1Y':
        dias_totales = 365
    elif hero_period == 'ALL':
        if transacciones:
            primer_fecha = datetime.date.fromisoformat(min(t.date_str for t in transacciones))
            dias_totales = max(7, (hoy - primer_fecha).days)
        else:
            dias_totales = 30
    else:
        hero_period = '30D'
        dias_totales = 30
        
    fecha_inicio = hoy - datetime.timedelta(days=dias_totales)
    
    # Calcular array diario completo para el periodo
    neto_previo = sum(t.amount for t in transacciones if t.date_str < fecha_inicio.isoformat())
    acumulado = total_inicial + neto_previo
    daily_data = []
    
    for i in range(dias_totales + 1):
        dia_str = (fecha_inicio + datetime.timedelta(days=i)).isoformat()
        acumulado += balance_diario.get(dia_str, 0)
        daily_data.append({'date': dia_str, 'val': acumulado})
        
    # Samplear a ~30 puntos max para que la curva de Bezier sea suave y fluida
    hero_chart_data = []
    num_samples = min(30, len(daily_data))
    if num_samples < len(daily_data):
        step = (len(daily_data) - 1) / (num_samples - 1)
        for i in range(num_samples - 1):
            idx = int(i * step)
            hero_chart_data.append(daily_data[idx])
        hero_chart_data.append(daily_data[-1]) # Asegurar que el último punto es hoy
    else:
        hero_chart_data = daily_data
        
    c_min_real = min(d['val'] for d in hero_chart_data)
    c_max_real = max(d['val'] for d in hero_chart_data)
    
    c_min = c_min_real
    c_max = c_max_real
    rango = c_max - c_min
    if rango == 0:
        c_max = c_min + 1
        c_min = c_min - 1
    else:
        # Añadir margen visual: 40% arriba y 10% abajo para una visibilidad máxima ahora que el selector está arriba
        c_max = c_max + (rango * 0.4)
        c_min = c_min - (rango * 0.1)
    
    # Generar Path SVG (ViewBox 1000x300)
    w = 1000
    h = 300
    padding_top = 20
    padding_bottom = 20
    usable_h = h - padding_top - padding_bottom
    puntos_len = len(hero_chart_data)
    dx = w / (puntos_len - 1)
    
    def get_y(val):
        return h - padding_bottom - ((val - c_min) / (c_max - c_min)) * usable_h
        
    points_for_js = []
    first_y = get_y(hero_chart_data[0]['val'])
    hero_path_d = f"M 0,{first_y}"
    points_for_js.append({'x': 0, 'y': first_y, 'val': hero_chart_data[0]['val'], 'date': hero_chart_data[0]['date']})
    
    for i in range(1, puntos_len):
        x_prev = (i - 1) * dx
        y_prev = get_y(hero_chart_data[i-1]['val'])
        x_curr = i * dx
        y_curr = get_y(hero_chart_data[i]['val'])
        
        # Puntos de control para curva suave
        cp1_x = x_prev + dx / 2
        cp1_y = y_prev
        cp2_x = x_curr - dx / 2
        cp2_y = y_curr
        
        hero_path_d += f" C {cp1_x},{cp1_y} {cp2_x},{cp2_y} {x_curr},{y_curr}"
        points_for_js.append({'x': x_curr, 'y': y_curr, 'val': hero_chart_data[i]['val'], 'date': hero_chart_data[i]['date']})
        
    # Cerrar path para el area
    hero_area_d = hero_path_d + f" L {w},{h} L 0,{h} Z"
    
    # Porcentaje de cambio respecto al inicio del periodo
    balance_inicio_periodo = daily_data[0]['val']
    if balance_inicio_periodo != 0:
        pct_change = ((saldo_total - balance_inicio_periodo) / abs(balance_inicio_periodo)) * 100
    else:
        pct_change = 0 if saldo_total == 0 else 100

    # Datos para los gráficos: Gastos e Ingresos agrupados por categoría
    categorias = list(srp.filter(CategoryDto, lambda c: c.user_oid == user_id))
    cat_map = {str(c.__oid__): c for c in categorias}
    
    dist_gastos = {}
    dist_ingresos = {}
    
    for t in transacciones:
        cat = cat_map.get(str(t.cat_oid))
        if cat:
            key = cat.name
            target_dict = dist_gastos if t.amount < 0 else dist_ingresos
            if key not in target_dict:
                target_dict[key] = {"total": 0, "color": cat.color, "icon": cat.icon}
            target_dict[key]["total"] += abs(t.amount)

    def format_donut_data(data_dict):
        total = sum(v["total"] for v in data_dict.values()) or 1
        result = []
        for nombre, datos in data_dict.items():
            result.append({
                "name": nombre,
                "amount": datos["total"],
                "color": datos["color"],
                "icon": datos["icon"],
                "pct": round(datos["total"] / total * 100, 1)
            })
        result.sort(key=lambda x: x["amount"], reverse=True)
        return result, sum(v["total"] for v in data_dict.values())

    donut_gastos, total_g = format_donut_data(dist_gastos)
    donut_ingresos, total_i = format_donut_data(dist_ingresos)

    # Formateo de saldo total para la tarjeta Hero
    saldo_total_entero = "{:,.0f}".format(int(saldo_total))
    saldo_total_decimal = "{:02d}".format(int(round(abs(saldo_total) * 100 % 100)))

    sust = {
        "cuentas": cuentas,
        "transacciones": transacciones[:3],
        "saldo_total": saldo_total,
        "saldo_total_entero": saldo_total_entero,
        "saldo_total_decimal": saldo_total_decimal,
        "income_mensual": income_mensual,
        "expense_mensual": expense_mensual,
        "income_semana": income_semana,
        "expense_semana": expense_semana,
        "savings_semana": savings_semana,
        "income_change_pct": income_change_pct,
        "expense_change_pct": expense_change_pct,
        "savings_change_pct": savings_change_pct,
        "chart_week": chart_week,
        "week_max": week_max,
        "chart_month": chart_month,
        "pad_inicio": pad_inicio,
        "mes_label": (["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"][req_month-1] + f" {req_year}") if current_user.language != 'en' else (["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"][req_month-1] + f" {req_year}"),
        "year_label": str(req_year),
        "prev_month": prev_month,
        "prev_year_m": prev_year_m,
        "next_month": next_month,
        "next_year_m": next_year_m,
        "prev_year": req_year - 1,
        "next_year": req_year + 1,
        "curr_month": req_month,
        "curr_year": req_year,
        "chart_year": chart_year,
        "year_max": year_max,
        "chart_patrimonio": chart_patrimonio,
        "wealth_max": wealth_max,
        "hero_period": hero_period,
        "pct_change": pct_change,
        "hero_path_d": hero_path_d,
        "hero_area_d": hero_area_d,
        "hero_chart_points": json.dumps(points_for_js),
        "c_min_real": c_min_real,
        "c_max_real": c_max_real,
        "resumen_cuentas": resumen_cuentas,
        "meta_objetivo": meta_objetivo,
        "donut_gastos": donut_gastos,
        "donut_ingresos": donut_ingresos,
        "total_g": total_g,
        "total_i": total_i,
    }
    return flask.render_template("dashboard.html", **sust)
