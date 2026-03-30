#!/bin/bash

echo "-----------------------------------------"
echo "      INICIANDO FLASH OCR PRO"
echo "-----------------------------------------"

# 1. Verificar si existe el entorno virtual
if [ ! -d ".venv" ]; then
    echo "[!] No se detecto el entorno virtual. Configurando por primera vez..."

    # En Ubuntu a veces necesitas instalar venv explicitamente: sudo apt install python3-venv
    python3 -m venv .venv

    if [ $? -ne 0 ]; then
        echo "[ERROR] No se pudo crear el entorno virtual. Asegurate de tener python3-venv instalado."
        exit 1
    fi
    echo "[+] Entorno .venv creado exitosamente."

    echo "[+] Instalando librerias desde requirements.txt..."
    ./.venv/bin/pip install --upgrade pip
    ./.venv/bin/pip install -r requirements.txt
fi

# 2. Lanzar la aplicacion
echo "[+] Iniciando aplicacion..."
echo "[INFO] La carga inicial del motor de IA puede tomar unos segundos."

# Ejecutamos con python3 desde el venv y & al final para que corra en segundo plano
./.venv/bin/python3 main.py &

echo "[OK] Aplicacion lanzada."
echo "-----------------------------------------"