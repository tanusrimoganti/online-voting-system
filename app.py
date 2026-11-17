
from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
from database import create_tables, get_db_connection
from functools import wraps
import os

app = Flask(__name__)

app.secret_key = os.environ.get(
    "SECRET_KEY", "development-key-change-before-deployment"
)

create_tables()


# Login protection
def login_required(route):
    @wraps(route)
    def wrapper(*args, **kwargs):
        if "student_id" not in session:
            return redirect(url_for("login"))
        return route(*args, **kwargs)
    return wrapper


# Home page
@app.route("/")
def home():
    return render_template("index.html")


# Student registration
@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip().lower()
        reg_no = request.form.get("registration_number", "").strip()
        password = request.form.get("password", "")

        if not all([name, email, reg_no, password]):
            flash("Please fill in all fields.")
            return redirect(url_for("register"))

        if len(password) < 8:
            flash("Password must contain at least 8 characters.")
            return redirect(url_for("register"))

        password_hash = generate_password_hash(password)

        connection = get_db_connection()

        try:
            connection.execute("""
                INSERT INTO students
                (name, email, registration_number, password_hash)
                VALUES (?, ?, ?, ?)
            """, (name, email, reg_no, password_hash))

            connection.commit()
            flash("Registration successful! Please login.")

            return redirect(url_for("login"))

        except Exception:
            flash("Email or registration number already exists.")
            return redirect(url_for("register"))

        finally:
            connection.close()

    return render_template("register.html")


# Student login
@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")

        connection = get_db_connection()

        student = connection.execute("""
            SELECT * FROM students WHERE email = ?
        """, (email,)).fetchone()

        connection.close()

        if student and check_password_hash(
            student["password_hash"], password
        ):

            session.clear()
            session["student_id"] = student["student_id"]
            session["student_name"] = student["name"]
            session["role"] = student["role"]

            return redirect(url_for("dashboard"))

        flash("Invalid email or password.")

    return render_template("login.html")


# Student dashboard
@app.route("/dashboard")
@login_required
def dashboard():
    return render_template(
        "dashboard.html",
        name=session["student_name"]
    )


# Logout
@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("home"))


if __name__ == "__main__":
    app.run(debug=True)
