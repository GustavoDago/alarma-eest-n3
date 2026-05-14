#!/bin/bash

# Script de configuración automática para Debian - Sistema de Timbre Escolar
# Uso: chmod +x setup_debian.sh && ./setup_debian.sh

set -e

INSTALL_DIR="$(cd "$(dirname "$0")" && pwd)"
SERVICE_FILE="$INSTALL_DIR/timbre-escolar.service"

echo "--------------------------------------------------------"
echo "🚀 Iniciando instalación del Timbre Escolar EEST N°3"
echo "   Directorio: $INSTALL_DIR"
echo "--------------------------------------------------------"

# 1. Actualizar repositorios e instalar dependencias base
echo ""
echo "📦 1/5 Actualizando paquetes del sistema..."
sudo apt update
sudo apt install -y python3 python3-pip python3-venv git

# 2. Configurar permisos para el Relé USB
echo ""
echo "🔌 2/5 Configurando permisos de puerto serial..."
sudo usermod -a -G dialout $USER
echo "✅ Usuario '$USER' agregado al grupo 'dialout'."

# 3. Crear Entorno Virtual
echo ""
echo "🐍 3/5 Creando entorno virtual de Python..."
if [ ! -d "$INSTALL_DIR/venv" ]; then
    python3 -m venv "$INSTALL_DIR/venv"
    echo "✅ Entorno virtual 'venv' creado."
else
    echo "ℹ️  El entorno virtual ya existe. Saltando..."
fi

# 4. Instalar dependencias de Python
echo ""
echo "📚 4/5 Instalando Flask, APScheduler y Pyserial..."
source "$INSTALL_DIR/venv/bin/activate"
pip install --upgrade pip
pip install -r "$INSTALL_DIR/timbre-escolar/requirements.txt"
echo "✅ Librerías instaladas correctamente."

# 5. Configurar servicio systemd (autoarranque)
echo ""
echo "⚙️  5/5 Configurando servicio de autoarranque..."

# Actualizar las rutas en el archivo .service según la instalación actual
TEMP_SERVICE="/tmp/timbre-escolar.service"
sed "s|User=.*|User=$USER|g" "$SERVICE_FILE" > "$TEMP_SERVICE"
sed -i "s|WorkingDirectory=.*|WorkingDirectory=$INSTALL_DIR/timbre-escolar|g" "$TEMP_SERVICE"
sed -i "s|ExecStart=.*|ExecStart=$INSTALL_DIR/venv/bin/python app.py|g" "$TEMP_SERVICE"

sudo cp "$TEMP_SERVICE" /etc/systemd/system/timbre-escolar.service
sudo systemctl daemon-reload
sudo systemctl enable timbre-escolar
echo "✅ Servicio 'timbre-escolar' habilitado para inicio automático."

echo ""
echo "--------------------------------------------------------"
echo "✨ INSTALACIÓN FINALIZADA CON ÉXITO ✨"
echo "--------------------------------------------------------"
echo ""
echo "📌 Pasos siguientes:"
echo "   1. Reiniciá tu sesión (logout/login) para activar permisos del relé."
echo "   2. Iniciá el servicio manualmente la primera vez:"
echo "      sudo systemctl start timbre-escolar"
echo "   3. Verificá que funcione:"
echo "      sudo systemctl status timbre-escolar"
echo "   4. Abrí un navegador en http://localhost:5000"
echo ""
echo "📋 Comandos útiles:"
echo "   Ver estado:     sudo systemctl status timbre-escolar"
echo "   Ver logs:       journalctl -u timbre-escolar -f"
echo "   Reiniciar:      sudo systemctl restart timbre-escolar"
echo "   Detener:        sudo systemctl stop timbre-escolar"
echo "--------------------------------------------------------"
