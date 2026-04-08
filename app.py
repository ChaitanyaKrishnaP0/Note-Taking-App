from flask import Flask, render_template, request, redirect, session
import sqlite3

app = Flask(__name__)
app.secret_key = "supersecretkey"  # required for session

def get_db():
    conn = sqlite3.connect("notes.db")
    conn.row_factory = sqlite3.Row
    return conn

# Initialize DB and tables
def init_db():
    conn = get_db()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS notes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            content TEXT,
            FOREIGN KEY(user_id) REFERENCES users(id)
        )
    """)
    conn.close()

init_db()

# Home page - show user's notes
@app.route("/")
def home():
    if "user_id" not in session:
        return redirect("/login")
    user_id = session["user_id"]
    conn = get_db()
    notes = conn.execute("SELECT * FROM notes WHERE user_id=?", (user_id,)).fetchall()
    conn.close()
    return render_template("index.html", notes=notes)

# Add a note
@app.route("/add", methods=["POST"])
def add():
    if "user_id" not in session:
        return redirect("/login")
    content = request.form["content"]
    user_id = session["user_id"]
    conn = get_db()
    conn.execute("INSERT INTO notes (user_id, content) VALUES (?, ?)", (user_id, content))
    conn.commit()
    conn.close()
    return redirect("/")

# Delete a note
@app.route("/delete/<int:id>")
def delete(id):
    if "user_id" not in session:
        return redirect("/login")
    user_id = session["user_id"]
    conn = get_db()
    # ensure users can't delete each other's notes
    conn.execute("DELETE FROM notes WHERE id=? AND user_id=?", (id, user_id))
    conn.commit()
    conn.close()
    return redirect("/")

# Login route
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        conn = get_db()
        user = conn.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password)).fetchone()
        conn.close()
        if user:
            session["user_id"] = user["id"]
            return redirect("/")
        else:
            return "Invalid username or password"
    return render_template("login.html")

# Logout
@app.route("/logout")
def logout():
    session.pop("user_id", None)
    return redirect("/login")

# Signup route
@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        conn = get_db()
        try:
            conn.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
            conn.commit()
        except sqlite3.IntegrityError:
            conn.close()
            return "Username already exists"
        conn.close()
        return redirect("/login")
    return render_template("signup.html")

if __name__ == "__main__":
    app.run(debug=True)