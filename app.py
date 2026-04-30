from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from functools import wraps
import sqlite3, os, hashlib

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "iilm-erp-secret-2025")
DB = "erp.db"

# ── DB INIT ──────────────────────────────────────────────────
def get_db():
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    c = conn.cursor()
    c.executescript("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        role TEXT NOT NULL DEFAULT 'student',
        roll_no TEXT,
        branch TEXT,
        year INTEGER DEFAULT 1
    );
    CREATE TABLE IF NOT EXISTS courses (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        code TEXT UNIQUE NOT NULL,
        name TEXT NOT NULL,
        credits INTEGER DEFAULT 3,
        faculty_id INTEGER
    );
    CREATE TABLE IF NOT EXISTS grades (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        student_id INTEGER,
        course_id INTEGER,
        marks INTEGER,
        grade TEXT
    );
    CREATE TABLE IF NOT EXISTS attendance (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        student_id INTEGER,
        course_id INTEGER,
        present INTEGER DEFAULT 0,
        total INTEGER DEFAULT 0
    );
    CREATE TABLE IF NOT EXISTS fees (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        student_id INTEGER,
        amount REAL,
        status TEXT DEFAULT 'Pending',
        due_date TEXT
    );
    """)
    # Seed admin
    pw = hashlib.sha256("admin123".encode()).hexdigest()
    try:
        c.execute("INSERT INTO users (name,email,password,role) VALUES (?,?,?,?)",
                  ("Admin", "admin@iilm.edu", pw, "admin"))
    except: pass
    # Seed students
    students = [
        ("Ashutosh Chakrawal","ashutosh@iilm.edu","student123","student","25SCS001","CSE",2),
        ("Rishabh Dhoundiyal","rishabh@iilm.edu","student123","student","25SCS002","CSE",2),
        ("Priya Sharma","priya@iilm.edu","student123","student","25SCS003","ECE",3),
        ("Ankit Verma","ankit@iilm.edu","student123","student","25SCS004","MBA",1),
    ]
    for s in students:
        pw2 = hashlib.sha256(s[2].encode()).hexdigest()
        try:
            c.execute("INSERT INTO users (name,email,password,role,roll_no,branch,year) VALUES (?,?,?,?,?,?,?)",
                      (s[0],s[1],pw2,s[3],s[4],s[5],s[6]))
        except: pass
    # Seed courses
    courses = [
        ("CS601","Cloud Computing",4),("CS602","Machine Learning",4),
        ("CS603","Database Systems",3),("CS604","Software Engineering",3),("CS605","Computer Networks",3),
    ]
    for co in courses:
        try: c.execute("INSERT INTO courses (code,name,credits) VALUES (?,?,?)", co)
        except: pass
    # Seed grades
    grade_map = {90:"A+",80:"A",70:"B+",60:"B",50:"C",0:"F"}
    marks_data = {1:[88,82,76,79,68], 2:[92,78,84,71,65], 3:[74,68,80,85,72], 4:[65,72,68,74,80]}
    for sid, marks_list in marks_data.items():
        for cid, mk in enumerate(marks_list, 1):
            g = next(v for k,v in sorted(grade_map.items(),reverse=True) if mk>=k)
            try: c.execute("INSERT INTO grades (student_id,course_id,marks,grade) VALUES (?,?,?,?)",(sid,cid,mk,g))
            except: pass
    # Seed fees
    for sid in range(1,5):
        try: c.execute("INSERT INTO fees (student_id,amount,status,due_date) VALUES (?,?,?,?)",
                       (sid, 85000, "Paid" if sid in [1,2] else "Pending","2025-06-30"))
        except: pass
    conn.commit(); conn.close()

# ── AUTH ─────────────────────────────────────────────────────
def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if "user_id" not in session:
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return decorated

def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if session.get("role") != "admin":
            flash("Admin access required","danger")
            return redirect(url_for("dashboard"))
        return f(*args, **kwargs)
    return decorated

# ── ROUTES ───────────────────────────────────────────────────
@app.route("/")
def index():
    if "user_id" in session:
        return redirect(url_for("dashboard"))
    return redirect(url_for("login"))

@app.route("/login", methods=["GET","POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        pw = hashlib.sha256(request.form["password"].encode()).hexdigest()
        conn = get_db()
        user = conn.execute("SELECT * FROM users WHERE email=? AND password=?", (email,pw)).fetchone()
        conn.close()
        if user:
            session["user_id"] = user["id"]
            session["name"]    = user["name"]
            session["role"]    = user["role"]
            session["email"]   = user["email"]
            return redirect(url_for("dashboard"))
        flash("Invalid credentials","danger")
    return render_template("login.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

@app.route("/dashboard")
@login_required
def dashboard():
    conn = get_db()
    if session["role"] == "admin":
        students = conn.execute("SELECT COUNT(*) as c FROM users WHERE role='student'").fetchone()["c"]
        courses  = conn.execute("SELECT COUNT(*) as c FROM courses").fetchone()["c"]
        pending  = conn.execute("SELECT COUNT(*) as c FROM fees WHERE status='Pending'").fetchone()["c"]
        all_students = conn.execute("SELECT * FROM users WHERE role='student'").fetchall()
        conn.close()
        return render_template("admin_dashboard.html",
                               students=students, courses=courses, pending_fees=pending,
                               all_students=all_students)
    else:
        uid = session["user_id"]
        user   = conn.execute("SELECT * FROM users WHERE id=?", (uid,)).fetchone()
        grades = conn.execute("""
            SELECT c.name, c.code, c.credits, g.marks, g.grade
            FROM grades g JOIN courses c ON g.course_id=c.id
            WHERE g.student_id=?""", (uid,)).fetchall()
        fees   = conn.execute("SELECT * FROM fees WHERE student_id=?", (uid,)).fetchone()
        total  = sum(g["marks"] for g in grades)
        cgpa   = round((total / (len(grades)*100)) * 10, 2) if grades else 0
        conn.close()
        return render_template("student_dashboard.html",
                               user=user, grades=grades, fees=fees, cgpa=cgpa)

@app.route("/admin/students")
@login_required
@admin_required
def admin_students():
    conn = get_db()
    students = conn.execute("SELECT * FROM users WHERE role='student' ORDER BY id").fetchall()
    conn.close()
    return render_template("admin_students.html", students=students)

@app.route("/admin/courses")
@login_required
@admin_required
def admin_courses():
    conn = get_db()
    courses = conn.execute("SELECT * FROM courses ORDER BY id").fetchall()
    conn.close()
    return render_template("admin_courses.html", courses=courses)

@app.route("/admin/fees")
@login_required
@admin_required
def admin_fees():
    conn = get_db()
    fees = conn.execute("""
        SELECT f.*, u.name, u.roll_no FROM fees f
        JOIN users u ON f.student_id=u.id ORDER BY f.id""").fetchall()
    conn.close()
    return render_template("admin_fees.html", fees=fees)

@app.route("/admin/add_student", methods=["POST"])
@login_required
@admin_required
def add_student():
    data = request.form
    pw = hashlib.sha256(data["password"].encode()).hexdigest()
    conn = get_db()
    try:
        conn.execute("INSERT INTO users (name,email,password,role,roll_no,branch,year) VALUES (?,?,?,?,?,?,?)",
                     (data["name"],data["email"],pw,"student",data["roll_no"],data["branch"],data["year"]))
        conn.commit(); flash("Student added successfully","success")
    except Exception as e:
        flash(f"Error: {e}","danger")
    conn.close()
    return redirect(url_for("admin_students"))

@app.route("/admin/update_fee/<int:fee_id>", methods=["POST"])
@login_required
@admin_required
def update_fee(fee_id):
    status = request.form["status"]
    conn = get_db()
    conn.execute("UPDATE fees SET status=? WHERE id=?", (status, fee_id))
    conn.commit(); conn.close()
    flash("Fee status updated","success")
    return redirect(url_for("admin_fees"))

@app.route("/grades")
@login_required
def grades():
    conn = get_db()
    uid = session["user_id"]
    grades = conn.execute("""
        SELECT c.name, c.code, c.credits, g.marks, g.grade
        FROM grades g JOIN courses c ON g.course_id=c.id
        WHERE g.student_id=?""", (uid,)).fetchall()
    conn.close()
    return render_template("grades.html", grades=grades)

@app.route("/health")
def health():
    return jsonify({"status": "healthy", "version": "1.0.0"})

if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=5000, debug=False)
