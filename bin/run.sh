#!/bin/bash
echo "==================================================="
echo "  Kashy Finance - Iniciando Servidor Local"
echo "==================================================="
echo ""
cd "$(dirname "$0")/../src"
echo "[+] Instalando dependencias necesarias..."
pip install -r requirements.txt
echo ""
echo "[+] Ejecutando el servidor de pruebas de Flask..."
flask run
