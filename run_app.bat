@echo off
setlocal
title Lanzador de Flash OCR

echo =========================================
echo       INICIANDO FLASH OCR PRO
echo =========================================

:: 1. Verificar si existe el entorno virtual
if not exist .venv (
    echo [!] No se detecto el entorno virtual. Configurando por primera vez...
    python -m venv .venv
    if %errorlevel% neq 0 (
        echo [ERROR] Python no esta instalado o no esta en el PATH.
        pause
        exit /b
    )
    echo [+] Entorno .venv creado con exito.

    echo [+] Instalando librerias necesarias...
    .\.venv\Scripts\python.exe -m pip install --upgrade pip
    .\.venv\Scripts\python.exe -m pip install -r requirements.txt
)

:: 2. Lanzar la aplicacion
echo [+] Iniciando aplicacion...
echo [INFO] La primera vez puede tardar unos segundos extra cargando la IA.
start /b .\.venv\Scripts\pythonw.exe main.py

echo [OK] Aplicacion lanzada en segundo plano.
echo =========================================
exit