from flask import Flask, render_template, request, redirect
from models import connect_db, create_tables
import os

app = Flask(__name__)
app.secret_key = "secret"

create_tables()

# ---------- INSERT PLAYS ----------
def insert_plays():
    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM plays")
    if cursor.fetchone()[0] == 0:
        plays = [
            ("Rango Se Pare", "13 Feb", "1:00 PM"),
            ("Umaj", "21 Aug", "5:00 PM"),
            ("Andhagharam", "15 Feb", "5:30 PM"),
            ("Nirvaan", "20 Feb", "3:00 PM"),
            ("Phir Milenge", "15 Feb", "7:00 PM")
        ]
        cursor.executemany(
            "INSERT INTO plays(name,date,time) VALUES(?,?,?)",
            plays
        )
        conn.commit()

    conn.close()

insert_plays()

# ---------- HOME ----------
@app.route('/')
def home():
    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM plays")
    plays = cursor.fetchall()

    conn.close()
    return render_template("plays.html", plays=plays)

# ---------- SEATS ----------
@app.route('/seats/<int:play_id>', methods=["GET", "POST"])
def seats(play_id):
    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("SELECT name FROM plays WHERE id=?", (play_id,))
    play = cursor.fetchone()

    if request.method == "POST":
        seats = request.form.get("seat")
        name = request.form.get("name")
        phone = request.form.get("phone")

        if not seats:
            conn.close()
            return "❌ Select seat first"

        seat_list = seats.split(",")

        for seat in seat_list:

            cursor.execute(
                "SELECT * FROM bookings WHERE play_id=? AND seat_number=?",
                (play_id, seat)
            )

            if cursor.fetchone():
                conn.close()
                return "❌ Seat already booked"

            if seat.startswith('A') or seat.startswith('B'):
                price = 500
            elif seat.startswith('C') or seat.startswith('D'):
                price = 300
            else:
                price = 200

            cursor.execute("""
                INSERT INTO bookings(play_id,seat_number,name,phone,price)
                VALUES(?,?,?,?,?)
            """, (play_id, seat, name, phone, price))

        conn.commit()
        conn.close()

        return redirect("/dashboard")

    cursor.execute(
        "SELECT seat_number FROM bookings WHERE play_id=?",
        (play_id,)
    )

    booked = [x[0] for x in cursor.fetchall()]

    conn.close()

    return render_template(
        "seats.html",
        booked=booked,
        play_name=play[0],
        play_id=play_id
    )

# ---------- DASHBOARD ----------
@app.route('/dashboard')
def dashboard():
    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, play_id, seat_number, name, phone, price
        FROM bookings
    """)

    data = cursor.fetchall()

    conn.close()

    return render_template("dashboard.html", data=data)

# ---------- UNBOOK ----------
@app.route('/unbook/<int:id>')
def unbook(id):
    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM bookings WHERE id=?", (id,))
    conn.commit()

    conn.close()

    return redirect("/dashboard")

# ---------- RUN (IMPORTANT FOR RENDER) ----------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
