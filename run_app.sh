#!/bin/bash

# Obtener la ruta del directorio donde está el script
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$DIR"

echo "-----------------------------------------"
echo "      INICIANDO FLASH OCR PRO"
echo "-----------------------------------------"

# 1. Verificar e instalar venv si no existe
if [ ! -d ".venv" ]; then
    echo "[!] Configurando entorno virtual por primera vez..."
    python3 -m venv .venv

    if [ $? -ne 0 ]; then
        echo "[ERROR] Fallo al crear el entorno. Intenta: sudo apt install python3-venv"
        exit 1
    fi

    echo "[+] Instalando dependencias..."
    ./.venv/bin/pip install --upgrade pip
    ./.venv/bin/pip install -r requirements.txt
fi

# 2. Ejecutar la aplicación
echo "[+] Lanzando Flash OCR..."
./.venv/bin/python3 main.py &

exit 0