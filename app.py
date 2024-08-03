from flask import Flask, request, render_template_string, redirect, url_for, flash, jsonify
import sqlite3
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Needed for flashing messages

# Path to the SQLite database
DATABASE = 'visitor_registration.db'

def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def create_table():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS registrations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            from_date TEXT NOT NULL,
            to_date TEXT NOT NULL,
            number_of_people INTEGER NOT NULL,
            adhaar_number TEXT NOT NULL,
            vehicle_number TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

@app.route('/')
def index():
    today = datetime.now().strftime('%Y-%m-%d')
    return render_template_string('''
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Visitor Registration</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                margin: 0;
                padding: 0;
                display: flex;
                flex-direction: column;
                align-items: center;
                background-color: #f9f9f9;
            }
            .container {
                border: 1px solid #ccc;
                padding: 20px;
                border-radius: 8px;
                box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
                background-color: #fff;
                width: 100%;
                max-width: 600px;
                margin-top: 20px;
            }
            h1 {
                text-align: center;
                margin-bottom: 20px;
            }
            .form-group {
                margin-bottom: 15px;
            }
            .form-group label {
                display: block;
                margin-bottom: 5px;
            }
            .form-group input {
                width: 100%;
                padding: 8px;
                box-sizing: border-box;
            }
            button {
                display: block;
                width: 100%;
                padding: 10px;
                background-color: #4CAF50;
                color: white;
                border: none;
                border-radius: 4px;
                cursor: pointer;
                font-size: 16px;
            }
            button:hover {
                background-color: #45a049;
            }
            .success-message {
                color: green;
                text-align: center;
                margin-bottom: 20px;
            }
        </style>
    </head>
    <body>
        <div class="container">
            {% with messages = get_flashed_messages(with_categories=true) %}
                {% if messages %}
                    {% for category, message in messages %}
                        <div class="{{ category }}-message success-message">
                            {{ message }}
                        </div>
                    {% endfor %}
                {% endif %}
            {% endwith %}
            
            <h1>Visitor Registration</h1>
            <form action="/submit" method="POST">
                <div class="form-group">
                    <label for="name">Name:</label>
                    <input type="text" id="name" name="name" required>
                </div>
                <div class="form-group">
                    <label for="from_date">From Date:</label>
                    <input type="date" id="from_date" name="from_date" min="{{ today }}" required>
                </div>
                <div class="form-group">
                    <label for="to_date">To Date:</label>
                    <input type="date" id="to_date" name="to_date" min="{{ today }}" required>
                </div>
                <div class="form-group">
                    <label for="number_of_people">Number of People:</label>
                    <input type="number" id="number_of_people" name="number_of_people" required>
                </div>
                <div class="form-group">
                    <label for="adhaar_number">Aadhaar Number:</label>
                    <input type="text" id="adhaar_number" name="adhaar_number" required>
                </div>
                <div class="form-group">
                    <label for="vehicle_number">Vehicle Number:</label>
                    <input type="text" id="vehicle_number" name="vehicle_number" required>
                </div>
                <button type="submit">Submit</button>
            </form>
            <a href="/registrations">View All Registrations</a>
        </div>

        <script>
            // JavaScript to ensure 'to_date' is after 'from_date'
            document.addEventListener('DOMContentLoaded', function() {
                const fromDateInput = document.getElementById('from_date');
                const toDateInput = document.getElementById('to_date');

                function validateDates() {
                    const fromDate = new Date(fromDateInput.value);
                    const toDate = new Date(toDateInput.value);

                    if (fromDate && toDate && fromDate > toDate) {
                        toDateInput.setCustomValidity('To Date must be after From Date.');
                    } else {
                        toDateInput.setCustomValidity('');
                    }
                }

                fromDateInput.addEventListener('change', validateDates);
                toDateInput.addEventListener('change', validateDates);
            });
        </script>
    </body>
    </html>
    ''', today=today)

@app.route('/submit', methods=['POST'])
def submit_registration():
    name = request.form['name']
    from_date = request.form['from_date']
    to_date = request.form['to_date']
    number_of_people = int(request.form['number_of_people'])
    adhaar_number = request.form['adhaar_number']
    vehicle_number = request.form['vehicle_number']

    if datetime.strptime(from_date, '%Y-%m-%d') > datetime.strptime(to_date, '%Y-%m-%d'):
        flash('To Date must be after From Date.', 'error')
        return redirect(url_for('index'))

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO registrations (name, from_date, to_date, number_of_people, adhaar_number, vehicle_number)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (name, from_date, to_date, number_of_people, adhaar_number, vehicle_number))
    conn.commit()
    conn.close()

    flash('Registration submitted successfully!', 'success')
    return redirect(url_for('index'))

@app.route('/registrations')
def registrations():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM registrations')
    all_registrations = cursor.fetchall()
    conn.close()

    return render_template_string('''
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>All Registrations</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                margin: 0;
                padding: 0;
                display: flex;
                flex-direction: column;
                align-items: center;
                background-color: #f9f9f9;
            }
            .container {
                border: 1px solid #ccc;
                padding: 20px;
                border-radius: 8px;
                box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
                background-color: #fff;
                width: 100%;
                max-width: 800px;
                margin-top: 20px;
            }
            h1 {
                text-align: center;
                margin-bottom: 20px;
            }
            table {
                width: 100%;
                border-collapse: collapse;
                margin-bottom: 20px;
            }
            table, th, td {
                border: 1px solid #ddd;
            }
            th, td {
                padding: 10px;
                text-align: left;
            }
            th {
                background-color: #f4f4f4;
            }
            a {
                display: block;
                width: 100%;
                text-align: center;
                padding: 10px;
                background-color: #4CAF50;
                color: white;
                text-decoration: none;
                border-radius: 4px;
                margin-top: 20px;
            }
            canvas {
                max-width: 100%;
                height: auto;
            }
            a:hover {
                background-color: #45a049;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>All Registrations</h1>
            <table>
                <thead>
                    <tr>
                        <th>Name</th>
                        <th>From Date</th>
                        <th>To Date</th>
                        <th>Number of People</th>
                        <th>Number of Days</th>
                        <th>Aadhaar Number</th>
                        <th>Vehicle Number</th>
                    </tr>
                </thead>
                <tbody>
                    {% for registration in registrations %}
                    <tr>
                        <td>{{ registration['name'] }}</td>
                        <td>{{ registration['from_date'] }}</td>
                        <td>{{ registration['to_date'] }}</td>
                        <td>{{ registration['number_of_people'] }}</td>
                        <td>{{ (datetime.strptime(registration['to_date'], '%Y-%m-%d') - datetime.strptime(registration['from_date'], '%Y-%m-%d')).days }}</td>
                        <td>{{ registration['adhaar_number'] }}</td>
                        <td>{{ registration['vehicle_number'] }}</td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
            <canvas id="visitorChart"></canvas>
            <a href="/">Register Another Visit</a>
        </div>
        <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
        <script>
            document.addEventListener('DOMContentLoaded', function() {
                fetch('/chart-data')
                    .then(response => response.json())
                    .then(data => {
                        const ctx = document.getElementById('visitorChart').getContext('2d');
                        new Chart(ctx, {
                            type: 'bar',
                            data: {
                                labels: data.dates,
                                datasets: [{
                                    label: 'Number of Visitors',
                                    data: data.counts,
                                    backgroundColor: 'rgba(75, 192, 192, 0.2)',
                                    borderColor: 'rgba(75, 192, 192, 1)',
                                    borderWidth: 1
                                }]
                            },
                            options: {
                                scales: {
                                    y: {
                                        beginAtZero: true,
                                        ticks: {
                                            stepSize: 1, // Ensure steps are whole numbers
                                            callback: function(value) {
                                                if (Number.isInteger(value)) {
                                                    return value;
                                                }
                                            }
                                        }
                                    }
                                }
                            }
                        });
                    });
            });
        </script>
    </body>
    </html>
    ''', registrations=all_registrations, datetime=datetime)

@app.route('/chart-data')
def chart_data():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT date(from_date) as date, SUM(number_of_people) as total_people
        FROM registrations
        GROUP BY date
        ORDER BY date
    ''')
    data = cursor.fetchall()
    conn.close()

    dates = [row['date'] for row in data]
    counts = [int(row['total_people']) for row in data]  # Ensure counts are integers

    return jsonify({'dates': dates, 'counts': counts})

if __name__ == '__main__':
    create_table()  # Ensure the table is created
    app.run(debug=True)

