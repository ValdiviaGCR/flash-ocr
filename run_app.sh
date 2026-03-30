#!/bin/bash

# 1. Función para verificar paquetes del sistema (Ubuntu/Debian)
instalar_dependencias_sistema() {
    echo "[!] Verificando dependencias del sistema operativo..."

    # Lista de paquetes necesarios
    paquetes=("python3-venv" "python3-tk" "libgl1-mesa-glx")
    faltantes=()

    for pkg in "${paquetes[@]}"; do
        if ! dpkg -l | grep -q "^ii  $pkg "; then
            faltantes+=("$pkg")
        fi
    done

    if [ ${#faltantes[@]} -gt 0 ]; then
        echo "[+] Necesito instalar: ${faltantes[*]}"
        echo "[?] Ingresa tu contraseña para autorizar la instalacion:"
        sudo apt update && sudo apt install -y "${faltantes[@]}"
    else
        echo "[OK] Dependencias del sistema ya instaladas."
    fi
}

echo "-----------------------------------------"
echo "      INICIANDO FLASH OCR PRO (LINUX)"
echo "-----------------------------------------"

# Ejecutar verificación de sistema
instalar_dependencias_sistema

# 2. Crear entorno virtual si no existe
if [ ! -d ".venv" ]; then
    echo "[!] Creando entorno virtual .venv..."
    python3 -m venv .venv

    echo "[+] Instalando librerias de Python..."
    ./.venv/bin/pip install --upgrade pip
    ./.venv/bin/pip install -r requirements.txt
fi

# 3. Lanzar la aplicacion
echo "[+] Lanzando Flash OCR..."
./.venv/bin/python3 ocr_linux.py &

echo "-----------------------------------------"
exit 0