from flask import Flask, render_template, request, jsonify, redirect, url_for
from functools import wraps
import sqlite3

app = Flask(__name__)

# Definindo o nome de usuário e senha (em um ambiente real, isso deve ser feito de forma mais segura)
USERNAME = 'admin'
PASSWORD = 'senha123'

# Função de autenticação básica
def check_auth(username, password):
    return username == USERNAME and password == PASSWORD

# Função para exigir login básico
def requires_auth(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        auth = request.authorization
        if not auth or not check_auth(auth.username, auth.password):
            return 'Acesso negado', 401, {'WWW-Authenticate': 'Basic realm="Login Required"'}
        return f(*args, **kwargs)
    return decorated_function

# Função para conectar ao banco de dados SQLite
def get_db_connection():
    conn = sqlite3.connect('reservations.db')
    conn.row_factory = sqlite3.Row
    return conn

# Criar a tabela de reservas (isso só precisa ser feito uma vez)
def create_table():
    conn = get_db_connection()
    conn.execute('''CREATE TABLE IF NOT EXISTS reservations
                     (date TEXT, time TEXT, name TEXT, service TEXT)''')
    conn.commit()
    conn.close()

# Chama a função para criar a tabela na primeira execução
create_table()

# Página principal
@app.route('/')
def index():
    return render_template('index.html')

# Rota para exibir as reservas (apenas acessível para o admin)
@app.route('/admin')
@requires_auth
def admin():
    conn = get_db_connection()
    reservations = conn.execute('SELECT * FROM reservations').fetchall()
    conn.close()
    return render_template('admin.html', reservations=reservations)

# Rota para obter horários disponíveis
@app.route('/available_slots', methods=['GET'])
def available_slots():
    date = request.args.get('date')
    all_slots = [f"{hour:02d}:{minute:02d}" for hour in range(9, 18) for minute in (0, 30)]
    
    # Consultar as reservas no banco de dados
    conn = get_db_connection()
    reservations = conn.execute('SELECT time FROM reservations WHERE date = ?', (date,)).fetchall()
    conn.close()
    
    reserved_slots = [reservation['time'] for reservation in reservations]
    available_slots = [slot for slot in all_slots if slot not in reserved_slots]
    
    return jsonify(available_slots=available_slots, reserved_slots=reserved_slots)

# Rota para fazer uma reserva
@app.route('/book', methods=['POST'])
def book():
    name = request.form.get('name')
    datetime = request.form.get('datetime')
    service = request.form.get('service')

    if not name or not datetime or not service:
        return jsonify(success=False, message="Nome, horário ou serviço não fornecidos corretamente.")
    
    date, time = datetime.split(' ')

    # Inserir a reserva no banco de dados
    conn = get_db_connection()
    existing_reservation = conn.execute('SELECT * FROM reservations WHERE date = ? AND time = ? AND service = ?',
                                       (date, time, service)).fetchone()
    
    if existing_reservation:
        return jsonify(success=False, message='Horário já reservado.')

    conn.execute('INSERT INTO reservations (date, time, name, service) VALUES (?, ?, ?, ?)', 
                 (date, time, name, service))
    conn.commit()
    conn.close()

    return jsonify(success=True, message=f'Reserva confirmada para {time} no dia {date} para o serviço {service}.')

if __name__ == '__main__':
    app.run(debug=True)
