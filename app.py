from flask import Flask, request, render_template, redirect, session
import psycopg2

app = Flask(__name__)
app.secret_key = "lab-secret-key"

conn = psycopg2.connect(
    host="localhost",
    database="sqllab",
    user="labuser",
    password="labpass"
)

# ---------------- LOGIN (SQLi VULNERABLE) ----------------
@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        u = request.form["username"]
        p = request.form["password"]

        cur = conn.cursor()
        # ❌ SQL INJECTION
        query = f"SELECT username, role FROM users WHERE username='{u}' AND password='{p}'"
        cur.execute(query)
        result = cur.fetchone()

        if result:
            session["user"] = result[0]
            session["role"] = result[1]
            return redirect("/dashboard")

    return render_template("login.html")

# ---------------- DASHBOARD ----------------
@app.route("/dashboard")
def dashboard():
    if "user" not in session:
        return redirect("/")
    return render_template(
        "dashboard.html",
        user=session["user"],
        role=session["role"]
    )

# ---------------- VIEW USERS (BROKEN AUTH) ----------------
@app.route("/users")
def users():
    cur = conn.cursor()
    cur.execute("SELECT username, role FROM users")
    data = cur.fetchall()
    return render_template("users.html", users=data, role=session.get("role"))

# ---------------- ADMIN DELETE (NO CHECK ❌) ----------------
@app.route("/delete/<username>")
def delete_user(username):
    cur = conn.cursor()
    cur.execute(f"DELETE FROM users WHERE username='{username}'")
    conn.commit()
    return redirect("/users")

# ---------------- CHAT (STORED XSS) ----------------
@app.route("/chat", methods=["GET", "POST"])
def chat():
    if "user" not in session:
        return redirect("/")

    cur = conn.cursor()

    if request.method == "POST":
        msg = request.form["message"]
        user = session["user"]

        # ❌ STORED XSS
        cur.execute(
            f"INSERT INTO messages (username, message) VALUES ('{user}','{msg}')"
        )
        conn.commit()

    cur.execute("SELECT username, message FROM messages")
    chats = cur.fetchall()
    return render_template("chat.html", chats=chats)

# ---------------- LOGOUT ----------------
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
