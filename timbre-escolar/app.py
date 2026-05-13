import json
import os
from flask import Flask, render_template, request, jsonify
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from relay_control import trigger_relay

app = Flask(__name__)
scheduler = BackgroundScheduler()

DATA_FILE = 'schedules.json'

def load_schedules():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r') as f:
            return json.load(f)
    return []

def save_schedules(schedules):
    with open(DATA_FILE, 'w') as f:
        json.dump(schedules, f, indent=4)

def ring_job(duration_seconds):
    print(f"⏰ [SCHEDULER] ¡Tocando el timbre automático por {duration_seconds} segundos!")
    trigger_relay(duration_seconds)

def schedule_jobs():
    scheduler.remove_all_jobs()
    schedules = load_schedules()
    for idx, sch in enumerate(schedules):
        time_parts = sch['time'].split(':')
        hour = time_parts[0]
        minute = time_parts[1]
        
        # Por defecto suena de Lunes a Viernes (mon-fri)
        days = sch.get('days', 'mon,tue,wed,thu,fri')
        
        scheduler.add_job(
            func=ring_job,
            trigger=CronTrigger(day_of_week=days, hour=hour, minute=minute),
            args=[sch.get('duration', 5)],
            id=str(idx),
            name=f"Timbre {sch['time']}"
        )

# Inicializar programador de tareas
schedule_jobs()
scheduler.start()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/schedules', methods=['GET'])
def get_schedules():
    return jsonify(load_schedules())

@app.route('/api/schedules', methods=['POST'])
def add_schedule():
    data = request.json
    schedules = load_schedules()
    schedules.append({
        'time': data['time'],
        'days': data.get('days', 'mon,tue,wed,thu,fri'),
        'duration': int(data.get('duration', 5))
    })
    # Ordenar por hora
    schedules.sort(key=lambda x: x['time'])
    save_schedules(schedules)
    schedule_jobs() # Recargar trabajos
    return jsonify({"status": "success"})

@app.route('/api/schedules/<int:idx>', methods=['DELETE'])
def delete_schedule(idx):
    schedules = load_schedules()
    if 0 <= idx < len(schedules):
        schedules.pop(idx)
        save_schedules(schedules)
        schedule_jobs() # Recargar trabajos
    return jsonify({"status": "success"})

@app.route('/api/ring', methods=['POST'])
def manual_ring():
    data = request.json
    duration = int(data.get('duration', 3))
    print(f"🛎️ [MANUAL] Activando timbre manual por {duration} segundos.")
    trigger_relay(duration)
    return jsonify({"status": "success"})

if __name__ == '__main__':
    # Ejecuta el servidor web en el puerto 5000 accesible desde la red local
    app.run(host='0.0.0.0', port=5000, debug=True, use_reloader=False)
