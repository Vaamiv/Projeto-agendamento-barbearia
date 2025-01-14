from flask import Flask, render_template, request, jsonify
import sqlite3

app = Flask(__name__)

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

# Rota para obter horários disponíveis e reservados
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
    try:
        name = request.form.get('name')
        datetime = request.form.get('datetime')
        service = request.form.get('service')

        # Log para depuração
        print(f"Recebido - Nome: {name}, Data/Hora: {datetime}, Serviço: {service}") 

        if not name or not datetime or not service:
            print("Erro: Nome, horário ou serviço não fornecidos corretamente.")
            return jsonify(success=False, message="Nome, horário ou serviço não fornecidos corretamente.")
        
        date, time = datetime.split(' ')

        # Log para verificação
        print(f"Separado - Data: {date}, Hora: {time}")

        # Inserir a reserva no banco de dados
        conn = get_db_connection()
        existing_reservation = conn.execute('SELECT * FROM reservations WHERE date = ? AND time = ? AND service = ?',
                                           (date, time, service)).fetchone()

        if existing_reservation:
            print("Erro: Horário já reservado.")
            return jsonify(success=False, message='Horário já reservado.')

        conn.execute('INSERT INTO reservations (date, time, name, service) VALUES (?, ?, ?, ?)', 
                     (date, time, name, service))
        conn.commit()
        conn.close()

        print(f"Reserva confirmada para {time} no dia {date} para o serviço {service}.")
        return jsonify(success=True, message=f'Reserva confirmada para {time} no dia {date} para o serviço {service}.')

    except Exception as e:
        print(f"Ocorreu um erro inesperado: {e}")
        return jsonify(success=False, message="Erro interno no servidor.")


if __name__ == '__main__':
    app.run(debug=True)
