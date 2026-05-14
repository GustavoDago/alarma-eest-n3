#!/bin/bash

# Script de configuración automática para Debian - Sistema de Timbre Escolar
# Uso: chmod +x setup_debian.sh && ./setup_debian.sh

echo "--------------------------------------------------------"
echo "🚀 Iniciando instalación del Timbre Escolar EEST N°3"
echo "--------------------------------------------------------"

# 1. Actualizar repositorios e instalar dependencias base
echo "📦 1/4 Actualizando paquetes del sistema..."
sudo apt update
sudo apt install -y python3 python3-pip python3-venv git

# 2. Configurar permisos para el Relé USB
echo "🔌 2/4 Configurando permisos de puerto serial..."
sudo usermod -a -G dialout $USER
echo "✅ Usuario agregado al grupo 'dialout'."

# 3. Crear Entorno Virtual
echo "🐍 3/4 Creando entorno virtual de Python..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo "✅ Entorno virtual 'venv' creado."
else
    echo "ℹ️ El entorno virtual ya existe. Saltando..."
fi

# 4. Instalar dependencias de Python
echo "📚 4/4 Instalando Flask, APScheduler y Pyserial..."
source venv/bin/activate
pip install --upgrade pip
if [ -f "timbre-escolar/requirements.txt" ]; then
    pip install -r timbre-escolar/requirements.txt
    echo "✅ Librerías instaladas correctamente."
else
    echo "❌ ERROR: No se encontró el archivo requirements.txt"
    exit 1
fi

echo "--------------------------------------------------------"
echo "✨ INSTALACIÓN FINALIZADA CON ÉXITO ✨"
echo "--------------------------------------------------------"
echo "Para iniciar el sistema:"
echo "  1. Reinicia tu sesión (log out y log in) para activar los permisos del relé."
echo "  2. Entra a la carpeta y activa el entorno: source venv/bin/activate"
echo "  3. Ejecuta la app: python timbre-escolar/app.py"
echo "--------------------------------------------------------"
