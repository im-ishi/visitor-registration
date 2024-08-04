import os
import sqlite3
from flask import Flask, request, render_template_string, redirect, url_for, flash, jsonify
from datetime import datetime
import logging

app = Flask(__name__)
app.secret_key = 'your_secret_key'

DATABASE = '/tmp/visitor_registration.db'

def get_db_connection():
    try:
        conn = sqlite3.connect(DATABASE)
        conn.row_factory = sqlite3.Row
        return conn
    except Exception as e:
        app.logger.error(f"Database connection failed: {e}")
        return None

def create_table():
    try:
        conn = get_db_connection()
        if conn:
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
            app.logger.info("Table 'registrations' created successfully.")
        else:
            app.logger.error("Failed to create table: database connection failed.")
    except Exception as e:
        app.logger.error(f"Table creation failed: {e}")

@app.before_request
def before_request():
    # Check and create the table if it doesn't exist
    create_table()

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
            background-color: #f4f4f4;
            margin: 0;
            padding: 0;
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100vh;
        }
        .container {
            background-color: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
        }
        h1 {
            margin-top: 0;
        }
        form {
            display: flex;
            flex-direction: column;
        }
        label {
            margin-top: 10px;
        }
        input {
            padding: 8px;
            margin-top: 5px;
            border: 1px solid #ccc;
            border-radius: 4px;
        }
        button {
            margin-top: 20px;
            padding: 10px;
            background-color: #28a745;
            color: white;
            border: none;
            border-radius: 4px;
            cursor: pointer;
        }
        button:hover {
            background-color: #218838;
        }
        a {
            margin-top: 10px;
            color: #007bff;
            text-decoration: none;
        }
        a:hover {
            text-decoration: underline;
        }
        .success-message {
            color: green;
            margin-top: 10px;
        }
        .error-message {
            color: red;
            margin-top: 10px;
        }
    </style>
</head>
<body>
    <div class="container">
        {% with messages = get_flashed_messages(with_categories=true) %}
            {% if messages %}
                {% for category, message in messages %}
                    <div class="{{ category }}-message">
                        {{ message }}
                    </div>
                {% endfor %}
            {% endif %}
        {% endwith %}
        <h1>Visitor Registration</h1>
        <form action="/submit" method="POST">
            <label for="name">Name:</label>
            <input type="text" id="name" name="name" required>
            
            <label for="from_date">From Date:</label>
            <input type="date" id="from_date" name="from_date" min="{{ today }}" required>
            
            <label for="to_date">To Date:</label>
            <input type="date" id="to_date" name="to_date" min="{{ today }}" required>
            
            <label for="number_of_people">Number of People:</label>
            <input type="number" id="number_of_people" name="number_of_people" required>
            
            <label for="adhaar_number">Aadhaar Number:</label>
            <input type="text" id="adhaar_number" name="adhaar_number" required>
            
            <label for="vehicle_number">Vehicle Number:</label>
            <input type="text" id="vehicle_number" name="vehicle_number" required>
            
            <button type="submit">Submit</button>
        </form>
        <a href="/registrations">View All Registrations</a>
    </div>
</body>
</html>
''', today=today)

@app.route('/submit', methods=['POST'])
def submit():
    try:
        name = request.form['name']
        from_date = request.form['from_date']
        to_date = request.form['to_date']
        number_of_people = request.form['number_of_people']
        adhaar_number = request.form['adhaar_number']
        vehicle_number = request.form['vehicle_number']

        conn = get_db_connection()
        if conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO registrations (name, from_date, to_date, number_of_people, adhaar_number, vehicle_number)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (name, from_date, to_date, number_of_people, adhaar_number, vehicle_number))
            conn.commit()
            conn.close()
            flash('Registration successful!', 'success')
        else:
            flash('Database connection failed!', 'error')
    except Exception as e:
        app.logger.error(f"Form submission failed: {e}")
        flash('An error occurred during registration. Please try again.', 'error')

    return redirect(url_for('index'))

@app.route('/registrations')
def registrations():
    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM registrations')
            all_registrations = cursor.fetchall()
        except Exception as e:
            app.logger.error(f"Fetching registrations failed: {e}")
            all_registrations = []
        finally:
            conn.close()
    else:
        all_registrations = []

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
            background-color: #f4f4f4;
            margin: 0;
            padding: 20px;
        }
        .container {
            background-color: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
        }
        h1 {
            margin-top: 0;
        }
        table {
            width: 100%;
            border-collapse: collapse;
            margin-top: 20px;
        }
        th, td {
            padding: 8px;
            text-align: left;
            border-bottom: 1px solid #ddd;
        }
        th {
            background-color: #f2f2f2;
        }
        a {
            margin-top: 20px;
            color: #007bff;
            text-decoration: none;
        }
        a:hover {
            text-decoration: underline;
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
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT date(from_date) as date, SUM(number_of_people) as total_people
                FROM registrations
                GROUP BY date
                ORDER BY date
            ''')
            data = cursor.fetchall()
        except Exception as e:
            app.logger.error(f"Fetching chart data failed: {e}")
            data = []
        finally:
            conn.close()

        dates = [row['date'] for row in data]
        counts = [int(row['total_people']) for row in data]  # Ensure counts are integers

        return jsonify({'dates': dates, 'counts': counts})
    else:
        return jsonify({'dates': [], 'counts': []})

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    app.run(host='0.0.0.0', port=8080, debug=True)

