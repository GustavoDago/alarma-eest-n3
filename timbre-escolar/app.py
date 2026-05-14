import json
import os
from datetime import datetime, date
from flask import Flask, render_template, request, jsonify
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from relay_control import trigger_relay

app = Flask(__name__)
scheduler = BackgroundScheduler()

CONFIG_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'config.json')

# ─── Funciones de Configuración ──────────────────────────────────────────────

def load_config():
    """Carga la configuración desde config.json."""
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {"duracion_por_defecto": 5, "horarios": [], "dias_sin_timbre": []}

def save_config(config):
    """Guarda la configuración en config.json."""
    with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=4, ensure_ascii=False)

# ─── Lógica de Exclusión ─────────────────────────────────────────────────────

def es_dia_sin_timbre(fecha=None):
    """Verifica si una fecha dada es fin de semana o está en la lista de días sin timbre."""
    if fecha is None:
        fecha = date.today()

    # Fin de semana (5 = sábado, 6 = domingo)
    if fecha.weekday() >= 5:
        return True, "Fin de semana"

    config = load_config()
    fechas_excluidas = config.get('dias_sin_timbre', [])
    fecha_str = fecha.isoformat()

    for dia in fechas_excluidas:
        if dia['fecha'] == fecha_str:
            return True, dia.get('motivo', 'Día sin timbre')

    return False, None

# ─── Trabajo del Relé ─────────────────────────────────────────────────────────

def ring_job(duration_seconds, etiqueta):
    """Ejecuta el timbre solo si hoy es un día hábil."""
    excluido, motivo = es_dia_sin_timbre()
    if excluido:
        print(f"🚫 [SCHEDULER] Timbre cancelado: {motivo}. No se activa '{etiqueta}'.")
        return

    print(f"⏰ [SCHEDULER] ¡Tocando el timbre! '{etiqueta}' por {duration_seconds} segundos.")
    trigger_relay(duration_seconds)

# ─── Programador de Tareas ────────────────────────────────────────────────────

def schedule_jobs():
    """Lee la configuración y programa todos los trabajos del timbre."""
    scheduler.remove_all_jobs()
    config = load_config()
    duracion_defecto = config.get('duracion_por_defecto', 5)

    for idx, horario in enumerate(config.get('horarios', [])):
        hora, minuto = horario['hora'].split(':')
        duracion = horario.get('duracion', duracion_defecto)
        etiqueta = horario.get('etiqueta', f"Timbre {horario['hora']}")

        scheduler.add_job(
            func=ring_job,
            trigger=CronTrigger(day_of_week='mon-fri', hour=int(hora), minute=int(minuto)),
            args=[duracion, etiqueta],
            id=f"timbre_{idx}",
            name=etiqueta,
            replace_existing=True
        )

    print(f"📋 [SCHEDULER] {len(config.get('horarios', []))} timbres programados.")

# ─── Inicialización ──────────────────────────────────────────────────────────

schedule_jobs()
scheduler.start()

# ─── Rutas Web ────────────────────────────────────────────────────────────────

@app.route('/')
def index():
    return render_template('index.html')

# ─── API: Estado ──────────────────────────────────────────────────────────────

@app.route('/api/status', methods=['GET'])
def get_status():
    """Devuelve el estado actual del sistema."""
    hoy = date.today()
    ahora = datetime.now()
    excluido, motivo = es_dia_sin_timbre(hoy)

    config = load_config()
    proximo = None

    if not excluido:
        hora_actual = ahora.strftime('%H:%M')
        for horario in sorted(config.get('horarios', []), key=lambda h: h['hora']):
            if horario['hora'] > hora_actual:
                proximo = horario
                break

    return jsonify({
        "fecha": hoy.isoformat(),
        "dia_semana": ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"][hoy.weekday()],
        "hora_actual": ahora.strftime('%H:%M:%S'),
        "activo": not excluido,
        "motivo_inactivo": motivo,
        "proximo_timbre": proximo,
        "total_horarios": len(config.get('horarios', []))
    })

# ─── API: Horarios ────────────────────────────────────────────────────────────

@app.route('/api/horarios', methods=['GET'])
def get_horarios():
    config = load_config()
    return jsonify(config.get('horarios', []))

@app.route('/api/horarios', methods=['POST'])
def add_horario():
    data = request.json
    config = load_config()

    nuevo = {
        'hora': data['hora'],
        'etiqueta': data.get('etiqueta', f"Timbre {data['hora']}"),
        'duracion': int(data.get('duracion', config.get('duracion_por_defecto', 5)))
    }

    config['horarios'].append(nuevo)
    config['horarios'].sort(key=lambda h: h['hora'])
    save_config(config)
    schedule_jobs()
    return jsonify({"status": "success"})

@app.route('/api/horarios/<int:idx>', methods=['DELETE'])
def delete_horario(idx):
    config = load_config()
    horarios = config.get('horarios', [])
    if 0 <= idx < len(horarios):
        eliminado = horarios.pop(idx)
        save_config(config)
        schedule_jobs()
        print(f"🗑️ [CONFIG] Horario eliminado: {eliminado['etiqueta']}")
    return jsonify({"status": "success"})

# ─── API: Días sin Timbre ─────────────────────────────────────────────────────

@app.route('/api/dias-sin-timbre', methods=['GET'])
def get_dias_sin_timbre():
    config = load_config()
    return jsonify(config.get('dias_sin_timbre', []))

@app.route('/api/dias-sin-timbre', methods=['POST'])
def add_dia_sin_timbre():
    data = request.json
    config = load_config()

    nuevo = {
        'fecha': data['fecha'],
        'motivo': data.get('motivo', 'Día sin timbre')
    }

    config.setdefault('dias_sin_timbre', []).append(nuevo)
    config['dias_sin_timbre'].sort(key=lambda d: d['fecha'])
    save_config(config)
    return jsonify({"status": "success"})

@app.route('/api/dias-sin-timbre/<int:idx>', methods=['DELETE'])
def delete_dia_sin_timbre(idx):
    config = load_config()
    dias = config.get('dias_sin_timbre', [])
    if 0 <= idx < len(dias):
        eliminado = dias.pop(idx)
        save_config(config)
        print(f"🗑️ [CONFIG] Día sin timbre eliminado: {eliminado['fecha']} ({eliminado['motivo']})")
    return jsonify({"status": "success"})

# ─── API: Control Manual ──────────────────────────────────────────────────────

@app.route('/api/ring', methods=['POST'])
def manual_ring():
    data = request.json
    duration = int(data.get('duration', 3))
    print(f"🛎️ [MANUAL] Activando timbre manual por {duration} segundos.")
    trigger_relay(duration)
    return jsonify({"status": "success"})

# ─── Inicio ───────────────────────────────────────────────────────────────────

if __name__ == '__main__':
    # Ejecuta el servidor web en el puerto 5000 accesible desde la red local
    app.run(host='0.0.0.0', port=5000, debug=True, use_reloader=False)
