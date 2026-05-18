#!/bin/bash
echo "==================================================="
echo "  Kashy Finance - Iniciando Servidor Local"
echo "==================================================="
echo ""
export PYTHONDONTWRITEBYTECODE=1
cd "$(dirname "$0")/../src"
echo "[+] Instalando dependencias necesarias..."
python3 -m pip install -r requirements.txt || python -m pip install -r requirements.txt
echo ""
echo "[+] Ejecutando el servidor de pruebas de Flask...
python3 -m flask run || python -m flask run"
