from flask import Flask, request, jsonify
from flask_cors import CORS
import mysql.connector
import os

app = Flask(__name__)
CORS(app)


def get_db():
    return mysql.connector.connect(
        host=os.environ.get("MYSQLHOST"),
        port=int(os.environ.get("MYSQLPORT", 3306)),
        user=os.environ.get("MYSQLUSER"),
        password=os.environ.get("MYSQLPASSWORD"),
        database=os.environ.get("MYSQLDATABASE")
    )

@app.route("/test-db")
def test_db():

    try:
        db = get_db()
        cursor = db.cursor()

        cursor.execute("SELECT 1")

        result = cursor.fetchone()

        cursor.close()
        db.close()

        return jsonify({
            "message": "MySQL connected successfully",
            "result": result
        })

    except Exception as error:

        return jsonify({
            "message": "MySQL connection failed",
            "error": str(error)
        }), 500
        
@app.route("/")
def home():
    return jsonify({
        "message": "Hotel Management System API is running"
    })


# -------------------------
# GET ALL ROOMS
# -------------------------

@app.route("/rooms", methods=["GET"])
def get_rooms():

    try:
        db = get_db()
        cursor = db.cursor(dictionary=True)

        cursor.execute("""
            SELECT *
            FROM rooms
            ORDER BY room_number
        """)

        rooms = cursor.fetchall()

        cursor.close()
        db.close()

        return jsonify(rooms)

    except Exception as error:

        return jsonify({
            "message": "Failed to load rooms",
            "error": str(error)
        }), 500

# -------------------------
# BOOK ROOM
# -------------------------

@app.route("/book", methods=["POST"])
def book_room():

    data = request.get_json()

    db = get_db()
    cursor = db.cursor(dictionary=True)

    try:

        cursor.execute("""
            SELECT *
            FROM rooms
            WHERE room_id = %s
            AND status = 'Available'
        """, (data["room_id"],))

        room = cursor.fetchone()

        if room is None:

            return jsonify({
                "message": "Room is not available"
            }), 400


        # Insert guest

        cursor.execute("""
            INSERT INTO guests
            (name, phone, email)
            VALUES (%s, %s, %s)
        """, (
            data["name"],
            data["phone"],
            data["email"]
        ))

        guest_id = cursor.lastrowid


        # Insert booking

        cursor.execute("""
            INSERT INTO bookings
            (guest_id, room_id, check_in, check_out)
            VALUES (%s, %s, %s, %s)
        """, (
            guest_id,
            data["room_id"],
            data["check_in"],
            data["check_out"]
        ))


        # Update room

        cursor.execute("""
            UPDATE rooms
            SET status = 'Booked'
            WHERE room_id = %s
        """, (
            data["room_id"],
        ))


        db.commit()

        return jsonify({
            "message": "Room booked successfully"
        })


    except Exception as error:

        db.rollback()

        return jsonify({
            "message": str(error)
        }), 500


    finally:

        cursor.close()
        db.close()


# -------------------------
# GET BOOKINGS
# -------------------------

@app.route("/bookings", methods=["GET"])
def get_bookings():

    db = get_db()
    cursor = db.cursor(dictionary=True)

    cursor.execute("""
        SELECT
            b.booking_id,
            g.name,
            r.room_number,
            r.room_type,
            b.check_in,
            b.check_out,
            b.status

        FROM bookings b

        JOIN guests g
        ON b.guest_id = g.guest_id

        JOIN rooms r
        ON b.room_id = r.room_id

        WHERE b.status = 'Booked'

        ORDER BY b.booking_id DESC
    """)

    bookings = cursor.fetchall()

    cursor.close()
    db.close()

    return jsonify(bookings)


# -------------------------
# CHECKOUT
# -------------------------

@app.route("/checkout/<int:booking_id>", methods=["PUT"])
def checkout(booking_id):

    db = get_db()
    cursor = db.cursor(dictionary=True)

    try:

        cursor.execute("""
            SELECT room_id
            FROM bookings

            WHERE booking_id = %s
            AND status = 'Booked'
        """, (
            booking_id,
        ))

        booking = cursor.fetchone()

        if booking is None:

            return jsonify({
                "message": "Booking not found"
            }), 404


        cursor.execute("""
            UPDATE bookings

            SET status = 'Checked Out'

            WHERE booking_id = %s
        """, (
            booking_id,
        ))


        cursor.execute("""
            UPDATE rooms

            SET status = 'Available'

            WHERE room_id = %s
        """, (
            booking["room_id"],
        ))


        db.commit()

        return jsonify({
            "message": "Checkout successful"
        })


    except Exception as error:

        db.rollback()

        return jsonify({
            "message": str(error)
        }), 500


    finally:

        cursor.close()
        db.close()


# -------------------------
# SERVER
# -------------------------

if __name__ == "__main__":

    port = int(os.environ.get("PORT", 5000))

    app.run(
        host="0.0.0.0",
        port=port
    )
