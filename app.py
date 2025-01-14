from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

# Simulação de banco de dados em memória
reservations = {}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/available_slots', methods=['GET'])
def available_slots():
    date = request.args.get('date')
    all_slots = [f"{hour:02d}:{minute:02d}" for hour in range(9, 18) for minute in (0, 30)]
    reserved_slots = reservations.get(date, [])
    available_slots = [slot for slot in all_slots if slot not in reserved_slots]
    return jsonify(available_slots=available_slots, reserved_slots=reserved_slots)

@app.route('/book', methods=['POST'])
def book():
    name = request.form['name']
    datetime = request.form['datetime']
    date, time = datetime.split(' ')
    
    if date not in reservations:
        reservations[date] = []
    
    if time in reservations[date]:
        return jsonify(success=False, message='Horário já reservado.')

    reservations[date].append(time)
    return jsonify(success=True, message=f'Reserva confirmada para {time} no dia {date}.')

if __name__ == '__main__':
    app.run(debug=True)
