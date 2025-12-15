from flask import Flask, request, render_template
import psycopg2

app = Flask(__name__)

conn = psycopg2.connect(
    host="localhost",
    database="sqllab",
    user="labuser",
    password="labpass"
)

@app.route('/')
def index():
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']

    cur = conn.cursor()

    # ❌ VULNERABLE SQL QUERY
    query = f"""
    SELECT * FROM users
    WHERE username = '{username}'
    AND password = '{password}'
    """

    print("[DEBUG] Executing:", query)

    cur.execute(query)
    result = cur.fetchone()

    if result:
        return "✅ Login Successful"
    else:
        return "❌ Login Failed"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
