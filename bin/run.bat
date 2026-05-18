@echo off
echo ===================================================
echo   Kashy Finance - Iniciando Servidor Local
echo ===================================================
echo.
cd %~dp0..\src
echo [+] Instalando dependencias necesarias...
python -m pip install -r requirements.txt
echo.
echo [+] Ejecutando el servidor de pruebas de Flask...
python -m flask run
pause
